import json
import sys

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect, Http404
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


class UserCreationView(CreateView):
    model = User
    template_name = 'jeugdzorg/user_form_create.html'
    form_class = UserCreationForm
    success_url = '/'

    def form_valid(self, form):
        context = self.get_context_data()

        user = form.save(commit=False)

        # profiel = Profiel(gebruiker=user)
        # profiel.voornaam = form.data.get('voornaam')
        # profiel.achternaam = form.data.get('achternaam')
        # profiel.tussenvoegsel = form.data.get('tussenvoegsel')
        # profiel.save(commit=False)
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

        messages.add_message(
            self.request,
            messages.INFO,
            "Een link om je account te activeren is verstuurd naar het opgegeven e-mailadres."
        )
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
            #return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
        # else:
        #     return HttpResponse('Activation link is invalid!')
        return super().get(request, *args, **kwargs)


class SearchView(UserPassesTestMixin, TemplateView):
    http_method_names = ['get', ]
    template_name = 'snippets/search_results.html'

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    # def get_context_data(self, **kwargs):
    #     s = ''
    #     for o in settings.SEARCH_MODELS:
    #         filename = '/opt/app/jeugdzorg/search_files/search_%s.html' % o.lower()
    #         if os.path.exists(filename):
    #             fp = open(filename, "r")
    #             content = fp.read()
    #             fp.close()
    #             soup = BeautifulSoup(content, "html.parser")
    #             results = soup.find_all("div", {"class": o.lower()})
    #             # print(o)
    #             print(results)
    #             for r in results:
    #                 # print(r)
    #                 result = r.find_all(text=re.compile(r'%s' % self.request.GET.get('q'), re.MULTILINE))
    #                 if result:
    #                     # print(r)
    #                     s += str(r)
    #
    #     print(s)
    #
    #
    #         # iv = SearchIndexView.as_view()(self.request, {'model': o})
    #
    #         # print(iv)
    #     profiel_lijst = Profiel.is_zichtbaar.all()
    #     rendered = render_to_string(self.get_template_names(), {'profiel_lijst': profiel_lijst})
    #     soup = BeautifulSoup(rendered, "html.parser")
    #     find = soup.find_all(text=re.compile(r'%s' % self.request.GET.get('q'), re.MULTILINE))
    #     # print(find)
    #     for f in find:
    #         # print(f.parents[0])
    #         for parent in f.parents:
    #             if parent is None:
    #                 pass
    #                 # print(parent)
    #             else:
    #                 pass
    #                 # print(parent.name)
    #     profiel_lijst = soup.find_all("div", {"class": "contact"})
    #     profiel_lijst_rendered = []
    #     for profiel in profiel_lijst:
    #         #print(profiel.find_all('dd'))
    #         results = profiel.find_all(text=re.compile(r'%s' % self.request.GET.get('q'), re.MULTILINE))
    #         # t = profiel.text.replace('De', '<de>De</de>')
    #         # profiel.text.replace_with(t)
    #         # print(profiel.text.replace('De', '<de>De</de>'))
    #         # print(profiel.parent({"class": "contact"}))
    #         if results:
    #             profiel_lijst_rendered.append(str(profiel))
    #             #print(str(profiel))
    #
    #
    #     data = super().get_context_data(**kwargs)
    #
    #     # print(profiel_lijst_rendered)
    #
    #     data.update({
    #         'profiel_lijst_rendered': profiel_lijst_rendered,
    #     })
    #     return data

    def get(self, request, *args, **kwargs):
        from lxml.html import fromstring
        s = ''
        indexes = get_search_indexes()
        for m in indexes:
            # print(current_milli_time() - ms)
            ms = current_milli_time()
            root = html.fromstring(m[1])
            ss = ''
            # e = root.find_class('profiel')
            # e = root.xpath('..//div[text()="%s"]' % self.request.GET.get('q'))

            for tags in root.iter('b'):  # root is the ElementTree object

                print(tags.tag)
                print(tags.tag)

            for r in root:
                for rr in r:
                # print(r.find_class('profiel'))
                #     print(r.text_content())
                    if self.request.GET.get('q').lower() in rr.text_content().lower():
                        # print(html.tostring(r))
                        ss += html.tostring(r).decode()
            # e = root.xpath('.//div[contains(text(),"%s")]' % self.request.GET.get('q'))
            # print(root)
            # print(e)
            # for tag in root.iter():
            #     if self.request.GET.get('q') in tag.text:
            #         print(tag)
            # soup = BeautifulSoup(m[1], "html.parser")
            # results = soup.find_all("div", {"class": m[0].lower()})
            # # print(current_milli_time() - ms)
            # for r in results:
            #     result = r.find_all(text=re.compile(r'%s' % self.request.GET.get('q'), re.IGNORECASE))
            #     if result:
            #         ss += str(r)
            if ss:
                s += '<div class="zoeken-paneel %s-lijst">%s</div>' % (
                    m[0].lower(),
                    ss,
                )
        # print(current_milli_time() - ms)
        return HttpResponse(s)

    # def get(self, request, *args, **kwargs):
    #     context = self.get_context_data(**kwargs)
    #
    #     rendered = render_to_string(self.get_template_names(), context)
    #     profiel_lijst = soup.find_all(text=re.compile('Reiskostenvergoeding'))
    #     profiel_lijst = soup.find_all("div", {"class": "contact", 'text': re.compile(r'skostenvergoedi', re.MULTILINE)})
    #     print(profiel_lijst)
    #     for profiel in profiel_lijst:
    #         # print(profiel.text)
    #         #results = profiel.find_all(text=re.compile(r'skostenvergoedi', re.MULTILINE))
    #         # t = profiel.text.replace('De', '<de>De</de>')
    #         # profiel.text.replace_with(t)
    #         # print(profiel.text.replace('De', '<de>De</de>'))
    #         # print(profiel.parent({"class": "contact"}))
    #         print(profiel)
    #         #if results:
    #         #    print(results)
    #
    #
    #     # print(soup)
    #
    #
    #
    #     return self.render_to_response(context)


class SearchIndexView(UserPassesTestMixin, TemplateView):
    http_method_names = ['get', ]
    template_name = 'snippets/search_results.html'

    def test_func(self):
        return auth_test(self.request.user, 'viewer')

    def get(self, request, *args, **kwargs):
        data = self.get_context_data(**kwargs)
        if kwargs.get('model') in settings.SEARCH_MODELS:
            filename = '/opt/app/jeugdzorg/search_files/search_%s.html' % kwargs.get('model')
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
