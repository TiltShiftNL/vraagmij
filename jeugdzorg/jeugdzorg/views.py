import json
import sys
import warnings

import sendgrid
from django.conf import settings
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.core.management import call_command
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render, resolve_url
from django.template.response import TemplateResponse
from django.urls import reverse, reverse_lazy
from django.utils.deprecation import RemovedInDjango21Warning
from django.views.decorators.csrf import csrf_protect
from django.views.generic import *
from sendgrid.helpers.mail import *
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404

from .auth import auth_test
from .forms import *


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

        # mail = Mail()
        # subject = "reset email subject"
        # body = "body"
        # sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        #
        # mail.from_email = Email("info@fixxx7.amsterdam.nl")
        # mail.reply_to = Email("mguikema@gmail.com")
        # mail.subject = subject
        # mail.add_content(Content("text/plain", body))
        # sg.client.mail.send.post(request_body=mail.get())

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
        data.update(self.kwargs);

        data['beeld'] = self.request.GET.get('beeld', 'alfabet')
        data['ordening'] = self.request.GET.get('ordening', 'oplopend')

        data['themas'] = Thema.objects.all

        if data['beeld'] not in ['alfabet', 'thema', 'aanbieder']:
            data['beeld'] = 'alfabet'

        data['list_template'] = 'snippets/regeling_list_%s.html' % data['beeld']

        return data


class RegelingDetail(DetailView):
    model = Regeling

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(self.kwargs)

        if data.get('slug'):
            # TODO: Mauricify
            data['parent'] = self.request.path.split('/regeling/')[0] + '/'
            data['thema'] = get_object_or_404(Thema, slug=data.get('slug'))

        return data


class ThemaList(ListView):
    model = Thema

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(self.kwargs);

        return data


class ThemaDetail(DetailView):
    model = Thema

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(self.kwargs);

        return data


class GebiedList(ListView):
    model = Gebied


class GebiedDetail(DetailView):
    model = Gebied


class ProfielList(UserPassesTestMixin, ListView):
    model = Profiel
    queryset = Profiel.is_zichtbaar.all()

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(self.kwargs);

        data['beeld'] = self.request.GET.get('beeld', 'alfabet')
        data['ordening'] = self.request.GET.get('ordening', 'oplopend')

        data['themas'] = Thema.objects.all
        data['organisaties'] = Organisatie.objects.all
        data['gebieden'] = Gebied.objects.all

        if data['beeld'] not in ['alfabet', 'thema', 'organisatie', 'gebied', 'recent']:
            data['beeld'] = 'alfabet'

        data['list_template'] = 'snippets/contact_list_%s.html' % data['beeld']

        return data


class ProfielDetail(UserPassesTestMixin, DetailView):
    model = Profiel
    queryset = Profiel.is_zichtbaar.all()

    def test_func(self):
        return auth_test(self.request.user, 'viewer')


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
    success_url = reverse_lazy('regelingen')

    def test_func(self):
        return auth_test(self.request.user, 'editor')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post = self.request.POST
        if post:
            data['voorwaarde'] = VoorwaardeFormSet(self.request.POST, self.request.FILES)
        else:
            data['voorwaarde'] = VoorwaardeFormSet()
        return data

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('update_regeling', kwargs={'pk': self.object.id})

    def form_valid(self, form):
        context = self.get_context_data()
        voorwaarde = context['voorwaarde']
        with transaction.atomic():
            self.object = form.save()
            if voorwaarde.is_valid():
                voorwaarde.instance = self.object
                voorwaarde.save()
        messages.add_message(self.request, messages.INFO, "De regeling '%s' is aangemaakt." % self.object.titel)
        return super(RegelingCreate, self).form_valid(form)


class RegelingUpdate(UserPassesTestMixin, UpdateView):
    model = Regeling
    form_class = RegelingModelForm
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
        else:
            data['voorwaarde'] = VoorwaardeFormSet(instance=self.object)
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        voorwaarde = context['voorwaarde']

        with transaction.atomic():
            self.object = form.save()
            if voorwaarde.is_valid():
                voorwaarde.instance = self.object
                voorwaarde.save()
        messages.add_message(self.request, messages.INFO, "De regeling '%s' is aangepast." % self.object.titel)
        return super(RegelingUpdate, self).form_valid(form)


class ProfielUpdateView(UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserModelForm

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        if self.request.POST.get('submit'):
            return self.request.POST.get('submit')
        return reverse_lazy('contacten')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post = self.request.POST
        if post:
            profiel_formset = UserFormSet(self.request.POST, self.request.FILES, instance=self.object)

            print(profiel_formset.errors)
            # for subform in profiel_formset.forms:
            #     subform.initial = {
            #         'email': self.object.email,
            #         'achternaam': self.object.last_name,
            #         'voornaam': self.object.first_name,
            #     }
            data['profiel'] = profiel_formset
        else:
            profiel_formset = UserFormSet(instance=self.object)
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
            else:
                print(profiel.errors)
                return self.form_invalid(form)


class EventView(View):
    http_method_names = ['post', ]

    def post(self, request, *args, **kwargs):
        event_list = json.loads(request.body)
        for event in event_list:
            try:
                event.update({'session_id': request.session.session_key})
                event_item = EventItem(**event)
                if request.user.is_authenticated:
                    event_item.user = request.user
                event_item.save()
            except:
                pass

        return JsonResponse({'status': 'ok'}, safe=False)


def logout(request):
    data = {
        'next_page': reverse_lazy('login'),
    }
    response = auth_views.logout(request, **data)

    if issubclass(HttpResponseRedirect, response.__class__):
        messages.add_message(
            request,
            messages.INFO,
            "Je bent nu uitgelogd."
        )

    return response


@csrf_protect
def password_reset_new_user(request, flow):
    from .context_processors import app_settings

    data = {
        'template_name': 'registration/reset_password.html',
        'password_reset_form': MailAPIPasswordResetForm,
        'email_template_name': 'registration/password_reset_email_%s.html' % flow,
        'post_reset_redirect': reverse_lazy('herstel_wachtwoord_klaar'),
        'subject_template_name': 'registration/password_reset_subject.txt',
        'extra_email_context': app_settings(),
    }
    if flow == 'new':
        data.update({
            'extra_context': {
                'email': request.GET.get('email'),
                'flow': flow,
            },

            'post_reset_redirect': reverse_lazy('wachtwoord_instellen_klaar'),
            'subject_template_name': 'registration/password_reset_subject_new.txt',
        })

    response = auth_views.password_reset(request, **data)
    return response


def password_reset_confirm_new_user(request, uidb64=None, token=None):
    # context =
    data = {
        'post_reset_redirect': reverse_lazy('login'),
        'template_name': 'registration/password_reset_confirm_new.html',
    }

    response = auth_views.password_reset_confirm(request, uidb64=uidb64, token=token, **data)

    if issubclass(HttpResponseRedirect, response.__class__):
        messages.add_message(
            request,
            messages.INFO,
            "Je wachtwoord is ingesteld. Log in met je nieuwe wachtwoord en vul daarna je profiel aan."
        )

    return response


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
