from django.views.generic import TemplateView
from django.views.generic import *
from .forms import *
from django.urls import reverse, reverse_lazy
from django import forms
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.management import call_command
import sys
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import select_template
from django.core.exceptions import ObjectDoesNotExist
from .mail import send_simple_message
from .auth import auth_test
from django.contrib import messages
from django.http import JsonResponse
import json
from django.conf import settings
import sendgrid
import os
from sendgrid.helpers.mail import *


class CheckUserModel(TemplateView):
    template_name = 'snippets/test.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['users'] = User.objects.all()
        return data


class ConfigView(LoginRequiredMixin, TemplateView):
    template_name = 'snippets/config.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        # sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        # from_email = Email("info@fixxx7.com")
        # to_email = Email("mguikema@gmail.com")
        # subject = "Sending with SendGrid is Fun"
        # content = Content("text/plain", "and easy to do anywhere, even with Python")
        # mail = Mail(from_email, subject, to_email, content)
        # response = sg.client.mail.send.post(request_body=mail.get())
        # print(response.status_code)
        # print(response.body)
        # print(response.headers)

        logs = [
            ['nginx error', '/var/log/nginx/error.log'],
            ['nginx access', '/var/log/nginx/access.log'],
            ['cron log', '/var/log/cron.log'],
        ]

        for l in logs:
            try:
                l.append(open(l[1], 'r'))
            except:
                l.append([])

        data['logs'] = [[log[0], log[1], [line.rstrip('\n') for line in log[2]]] for log in logs]

        return data


class RegelingList(ListView):
    model = Regeling

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['beeld'] = self.request.GET.get('beeld', 'alfabet')
        
        data['themas'] = Thema.objects.all
        
        if data['beeld'] not in ['alfabet', 'thema', 'aanbieder']:
            data['beeld'] = 'alfabet'

        data['list_template'] = 'snippets/regeling_list_%s.html' % data['beeld']

        return data


class RegelingDetail(DetailView):
    model = Regeling


class ThemaList(ListView):
    model = Thema


class ThemaDetail(DetailView):
    model = Thema


class ContactList(ListView):
    model = Contact
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['beeld'] = self.request.GET.get('beeld', 'alfabet')
        
        data['themas'] = Thema.objects.all
        data['organisaties'] = Organisatie.objects.all
        
        if data['beeld'] not in ['alfabet', 'thema', 'organisatie']:
            data['beeld'] = 'alfabet'

        data['list_template'] = 'snippets/contact_list_%s.html' % data['beeld']

        return data


class ProfielList(UserPassesTestMixin, ListView):
    model = Profiel

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['beeld'] = self.request.GET.get('beeld', 'alfabet')

        data['themas'] = Thema.objects.all
        data['organisaties'] = Organisatie.objects.all

        if data['beeld'] not in ['alfabet', 'thema', 'organisatie']:
            data['beeld'] = 'alfabet'

        data['list_template'] = 'snippets/contact_list_%s.html' % data['beeld']

        return data


class ContactDetail(DetailView):
    model = Contact


class ProfielDetail(UserPassesTestMixin, DetailView):
    model = Profiel

    def test_func(self):
        return auth_test(self.request.user, 'viewer')


class ContactUpdate(TemplateView):
    model = Contact
    template_name = 'jeugdzorg/contact_form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data['themas'] = Thema.objects.all
        data['organisaties'] = Organisatie.objects.all

        return data


class RegelingDelete(UserPassesTestMixin, DeleteView):
    model = Regeling
    success_url = reverse_lazy('regelingen')

    def test_func(self):
        return auth_test(self.request.user, 'editor')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        return data

    def delete(self, request, *args, **kwargs):

        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        messages.add_message(self.request, messages.INFO, "De regeling '%s' is verwijderd." % self.object.titel)
        self.object.delete()
        return HttpResponseRedirect(success_url)


class RegelingCreate(UserPassesTestMixin, CreateView):
    model = Regeling
    form_class = RegelingModelForm
    #fields = ['titel', 'samenvatting', 'bron', 'aanvraag_url', 'bron_url', 'startdatum', 'einddatum']
    success_url = reverse_lazy('regelingen')

    def test_func(self):
        return auth_test(self.request.user, 'editor')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post = self.request.POST
        if post:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST, self.request.FILES)
            data['dfs'] = ThemaFormSet(self.request.POST, self.request.FILES)
            data['crfs'] = ContactNaarRegelingFormSet(self.request.POST, self.request.FILES)

        else:
            data['voorwaarde'] = VoorwaardeFormSet()
            data['dfs'] = ThemaFormSet()
            data['crfs'] = ContactNaarRegelingFormSet()
        return data

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        context = self.get_context_data()
        voorwaarde = context['voorwaarde']
        crfs = context['crfs']
        dfs = context['dfs']
        with transaction.atomic():
            self.object = form.save()
            if voorwaarde.is_valid():
                voorwaarde.instance = self.object
                voorwaarde.save()
            if crfs.is_valid():
                crfs.instance = self.object
                crfs.save()
            if dfs.is_valid():
                dfs.instance = self.object
                dfs.save()
        messages.add_message(self.request, messages.INFO, "De regeling '%s' is aangemaakt." % self.object.titel)
        return super(RegelingCreate, self).form_valid(form)


class RegelingUpdate(UserPassesTestMixin, UpdateView):
    model = Regeling
    form_class = RegelingModelForm
    #fields = ['titel', 'samenvatting', 'bron', 'aanvraag_url', 'bron_url', 'startdatum', 'einddatum']
    success_url = reverse_lazy('regelingen')

    def test_func(self):
        return auth_test(self.request.user, 'editor')

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post = self.request.POST
        if post:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST, self.request.FILES, instance=self.object)
            data['dfs'] = ThemaFormSet(self.request.POST, self.request.FILES, instance=self.object)
            data['crfs'] = ContactNaarRegelingFormSet(self.request.POST, self.request.FILES, instance=self.object)

        else:
            data['voorwaarde'] = VoorwaardeFormSet(instance=self.object)
            data['dfs'] = ThemaFormSet(instance=self.object)
            data['crfs'] = ContactNaarRegelingFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        voorwaarde = context['voorwaarde']
        crfs = context['crfs']
        dfs = context['dfs']
        with transaction.atomic():
            self.object = form.save()
            if voorwaarde.is_valid():
                voorwaarde.instance = self.object
                voorwaarde.save()
            if crfs.is_valid():
                crfs.instance = self.object
                crfs.save()
            if dfs.is_valid():
                dfs.instance = self.object
                dfs.save()

        messages.add_message(self.request, messages.INFO, "De regeling '%s' is aangepast." % self.object.titel)
        return super(RegelingUpdate, self).form_valid(form)


class ProfielUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserModelForm

    def test_func(self):
        return self.request.user == self.get_object()

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('update_profiel')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post = self.request.POST
        if post:
            print(post)
            profiel_formset = UserFormSet(self.request.POST, self.request.FILES, instance=self.object)
            # for subform in profiel_formset.forms:
            #     subform.initial = {
            #         'email': self.object.email,
            #         'achternaam': self.object.last_name,
            #         'voornaam': self.object.first_name,
            #     }
            data['profiel'] = profiel_formset
        else:
            profiel_formset = UserFormSet(instance=self.object)
            # for subform in profiel_formset.forms:
            #     subform.initial = {
            #         'email': self.object.email,
            #         'achternaam': self.object.last_name,
            #         'voornaam': self.object.first_name,
            #     }
            data['profiel'] = profiel_formset
            data['object'] = self.object
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        profiel = context['profiel']
        with transaction.atomic():
            self.object = form.save()
            if profiel.is_valid():
                profiel.instance = self.object
                profiel.save()

        messages.add_message(self.request, messages.INFO, "Je profiel is aangepast.")
        return super().form_valid(form)


class EventView(View):
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        event_list = json.loads(request.body)
        for event in event_list:
            try:
                event_item = EventItem(**event)
                if request.user:
                    event_item.user = request.user
                event_item.save()
            except:
                pass

        return JsonResponse({'status': 'ok'}, safe=False)


@staff_member_required
def dump_jeugdzorg(request):
    sysout = sys.stdout
    fname = "%s-%s.json" % ('jeugdzorg', settings.SOURCE_COMMIT.strip())
    response = HttpResponse(content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=%s' % fname

    sys.stdout = response
    call_command('dumpdata', 'jeugdzorg', '--indent=4')
    sys.stdout = sysout

    # send_simple_message()

    return response


@staff_member_required
def load_jeugdzorg(request):
    if request.method == 'POST':
        form = UploadJeugdzorgFixtureFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request.FILES['file'])
            return HttpResponseRedirect('%s?success=1' % reverse('loadjeugdzorg'))
    else:
        form = UploadJeugdzorgFixtureFileForm()
    return render(request, 'snippets/upload_fixture.html', {'form': form})



