import json
import sys

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.http import JsonResponse, response
from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.views.decorators.csrf import csrf_protect
from django.views.generic import *
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .tokens import account_activation_token
from django.contrib.auth import models as auth_models
from bs4 import BeautifulSoup
from django.http import HttpResponse
import re
import time
from lxml import etree, html
import lxml
import socket
from .utils import *
from jeugdzorg.context_processors import app_settings
from .auth import auth_test
from .forms import *

current_milli_time = lambda: int(round(time.time() * 1000))


def get_search_indexes(models=None):
    out = []
    if not models:
        models = settings.SEARCH_MODELS
    for m in models:
        filename = '/opt/app/jeugdzorg/search_files/search_%s.html' % m.lower()
        if os.path.exists(filename):
            fp = open(filename, "r")
            content = fp.read()
            fp.close()
            out.append([m, content])
    return out


class RebuildCrontabsView(UserPassesTestMixin, View):
    http_method_names = ['get', ]
    template_name = 'admin/rebuild_crontabs_done.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request, *args, **kwargs):
        call_command('create_crontabs')
        time.sleep(5)
        messages.add_message(self.request, messages.INFO, "De crobtabs zijn vernieud." )
        return HttpResponseRedirect('/admin/')


class ConfigView(UserPassesTestMixin, TemplateView):
    template_name = 'snippets/config.html'

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        logs = [
            # ['hostfile', '/etc/hosts'],
            ['crontab', '/etc/cron.d/crontab'],
            # ['nginx error', '/var/log/nginx/error.log'],
            # ['nginx access', '/var/log/nginx/access.log'],
            ['cron log', '/var/log/cron.log'],
        ]

        envvars = ['%s: %s' % (k, v) for k, v in os.environ.items()]

        for l in logs:
            try:
                l.append(open(l[1], 'r'))
            except:
                l.append([])

        data['logs'] = [[log[0], log[1], [line.rstrip('\n') for line in log[2]]] for log in logs]
        data['envvars'] = envvars

        data['int_id'] = get_container_int()

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
        
        data['ordening'] = self.request.GET.get('ordening', 'oplopend')

        return data


class ThemaDetail(DetailView):
    model = Thema

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(self.kwargs)

        return data


class PaginaDetail(DetailView):
    model = Pagina
    queryset = Pagina.is_actief.all()


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
            
        if data['beeld'] == 'recent' and not self.request.GET.get('ordening'):
            data['ordening'] = 'aflopend'

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


class ProfielConnectToggle(UserPassesTestMixin, View):
    http_method_names = ['post', ]
    data_types = [
        'Regeling',
    ]
    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def post(self, request, *args, **kwargs):

        out = {'status': 'toegevoegd'}
        data = json.loads(request.body)
        if not data.get('connect_type') or not data.get('profiel_id') or not data.get('connect_id'):
            raise Http404
        if data.get('connect_type') not in self.data_types:
            raise Http404
        connect_cls = getattr(sys.modules[__name__], data.get('connect_type'))
        profiel = get_object_or_404(Profiel, id=data.get('profiel_id'))
        connect = get_object_or_404(connect_cls, id=data.get('connect_id'))
        connect_related = getattr(profiel, '%s_lijst' % data.get('connect_type').lower())
        connect_data = dict(profiel=profiel)
        connect_data[data.get('connect_type').lower()] = connect
        if connect in connect_related.all():
            remove = connect_related.through.objects.get(**connect_data)
            remove.delete()
            out['status'] = 'verwijderd'
        else:
            add = connect_related.through(**connect_data)
            add.save()
            out['status'] = 'toegevoegd'
        return JsonResponse(out, safe=False)


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


class UserCreationView(CreateView):
    model = User
    template_name = 'jeugdzorg/user_form_create.html'
    form_class = UserCreationForm
    success_url = '.?aangemaakt=1'

    def form_valid(self, form):
        context = self.get_context_data()

        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        data = {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'token': account_activation_token.make_token(user),
        }
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        body = render_to_string('registration/user_registration_activation_email.txt', data)
        if settings.ENV == 'develop':
            print(body)
        to_email = form.cleaned_data.get('email')
        subject = 'VraagMij account activatie.'
        email = Mail(Email('noreply@%s' % current_site.domain), subject, Email(to_email), Content("text/plain", body))
        sg.client.mail.send.post(request_body=email.get())
        return super().form_valid(form)


class UserActivationView(TemplateView):
    template_name = 'registration/user_registration_confirmation.html'

    def get(self, request, *args, **kwargs):
        try:
            uid = force_text(urlsafe_base64_decode(self.kwargs['uidb64']))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and account_activation_token.check_token(user, self.kwargs['token']):
            user.is_active = True
            user.save()
            profiel = Profiel(
                gebruiker=user,
                voornaam=user.voornaam,
                achternaam=user.achternaam,
                tussenvoegsel=user.tussenvoegsel,
                email=user.email,
                seconden_niet_gebruikt=(60 * 60 * 24 * 30 * 12),
                zichtbaar=True,
            )
            profiel.save()
            viewer_group = auth_models.Group.objects.filter(name='viewer')
            if viewer_group:
                user.groups.add(viewer_group[0])
            # login(request, user)
            messages.add_message(self.request, messages.INFO, "Je account is aangemaakt.")
            return redirect(reverse_lazy('login'))
        return super().get(request, *args, **kwargs)


class SearchView(UserPassesTestMixin, TemplateView):
    http_method_names = ['get', ]
    template_name = 'search/search_result.html'

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        data.update({
            'search': True,
            'model_list': [
                ('profiel', Profiel.is_zichtbaar.all(), ),
                ('regeling', Regeling.objects.all(), ),
                ('thema', Thema.objects.all(), ),
            ]
        })

        return data


class SearchIndexView(UserPassesTestMixin, TemplateView):
    http_method_names = ['get', ]
    template_name = 'snippets/search_results.html'

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def get(self, request, *args, **kwargs):
        data = self.get_context_data(**kwargs)

        filename = '/opt/app/jeugdzorg/search_files/search.html'
        if os.path.exists(filename):
            fp = open(filename, "r")
            content = fp.read()
            fp.close()
            return HttpResponse(content)

        raise Http404


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

            #print(profiel_formset.errors)
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


class GebruikersToevoegenView(UserPassesTestMixin, FormView):
    template_name = 'snippets/gebruikers_toevoegen.html'
    form_class = GebruikersToevoegenForm
    success_url = reverse_lazy('gebruikers_toevoegen')

    def test_func(self):
        return auth_test(self.request.user, 'beheergebruikers')

    def form_valid(self, form):
        domeinen = list(set([dd for d in Organisatie.objects.all() for dd in d.email_domeinen_lijst()]))
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        print(domeinen)
        validator = EmailValidator(whitelist=domeinen)
        print(form.data.get('gebruikers_lijst'))
        email_adressen = list(
            set([e.strip() for e in form.data.get('gebruikers_lijst').split(',')])
        )
        print(email_adressen)
        for email in email_adressen:
            valid = validator(email)
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        # print(self.form_valid(self.f))

        return super().post(request, *args, **kwargs)


class GebruikerUitnodigenView(UserPassesTestMixin, FormView):
    form_class = GebruikerUitnodigenForm
    template_name = 'form/gebruiker_uitnodigen.html'

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({
            'form': GebruikerUitnodigenForm(self.request.POST)
        })
        return data

    def form_valid(self, form):
        site = Site.objects.get_current()

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        data = {
            'naam': self.request.user.profiel.naam_volledig
        }
        data.update(app_settings())

        body = render_to_string('email/gebruiker_uitnodigen.txt', context=data, request=self.request)
        body_html = render_to_string('email/gebruiker_uitnodigen.html', data)
        subject = 'VraagMij uitnodiging'

        mail = Mail(
            Email('noreply@%s' % site.domain),
            subject,
            Email(form.cleaned_data.get('email')),
            Content("text/plain", body)
        )
        mail.add_content(Content("text/html", body_html))
        if settings.ENV != 'develop':
            sg.client.mail.send.post(request_body=mail.get())
        else:
            print(body)
        return super().form_valid(form)

    def get_success_url(self):
        return '%s?success=1' % reverse_lazy('gebruiker_uitnodigen')


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
        'set_password_form': SetPasswordForm,
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
