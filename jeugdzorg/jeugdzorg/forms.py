from django import forms
from django.forms import widgets
from .models import *
from django.core.management import call_command
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm
from django.forms.models import BaseInlineFormSet
import sendgrid
import os
from sendgrid.helpers.mail import *
from django.conf import settings
from django.template import loader
from itertools import chain

class UploadJeugdzorgFixtureFileForm(forms.Form):
    file = forms.FileField(
        label='Upload jeugdzorg.json'
    )


def handle_uploaded_file(f):
    with open('/opt/file_upload/jeugdzorg.json', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    call_command('loaddata', '/opt/file_upload/jeugdzorg.json', app_label='jeugdzorg')


class MailAPIPasswordResetForm(PasswordResetForm):
    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):

        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)

        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email(from_email)
        to_email = Email(to_email)

        mail = Mail(from_email, subject, to_email, body)
        response = sg.client.mail.send.post(request_body=mail.get())
        print(response.status_code)
        print(response.body)
        print(response.headers)

        pass



class RegelingModelForm(forms.ModelForm):
    class Meta:
        model = Regeling
        exclude = ['contact', ]
        widgets = {
            'startdatum': widgets.DateInput(
                attrs={'type': 'date'},
            ),
            'einddatum': widgets.DateInput(
                attrs={'type': 'date'},
            ),
        }
        # fields = ['titel', 'samenvatting', 'bron', 'aanvraag_url', 'bron_url', 'startdatum', 'einddatum']


class CustomField(forms.ModelMultipleChoiceField):
    widget = widgets.CheckboxSelectMultiple(attrs={'class': 'choices inlineformset-checkbox'})

    # def save_form_data(self):




class ProfielModelForm(forms.ModelForm):

    # thema = forms.ModelMultipleChoiceField(
    #     required=True,
    #     widget=widgets.CheckboxSelectMultiple(attrs={'class': 'choices inlineformset-checkbox'}),
    # )
    # themas = forms.MultipleChoiceField(
    #     required=False,
    #     widget=forms.CheckboxSelectMultiple(attrs={'class': 'choices inlineformset-checkbox'}),
    #     choices=list((thema.id, thema.titel) for thema in Thema.objects.all()),
    # )

    class Meta:
        model = Profiel
        exclude = []
        # fields = ['thema_lijst', ]
        # widgets = {
        #     'thema_lijst': widgets.CheckboxSelectMultiple(attrs={'class': 'choices inlineformset-checkbox'}),
        # }

    def save_m2m(self):
        pass
    # def save(self, commit=True):
    #     cleaned_data = self.cleaned_data
    #     exclude = self._meta.exclude
    #     fields = self._meta.fields
    #     opts = self.instance._meta
    #
    #     print(self.instance)
    #     print(cleaned_data)
    #     print(fields)
    #     print('opts')
    #     print(type(opts))
    #     super().save(commit)


class UserModelForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ['email', ]
        exclude = [
            'password',
            'is_superuser',
            'is_active',
            'is_staff',
            'date_joined',
            'last_login',
            'user_permissions',
            'groups',
        ]
        widgets = {
            'email': forms.HiddenInput,
        }

    # def _save_m2m(self):
    #     print('---')
    #     cleaned_data = self.cleaned_data
    #     exclude = self._meta.exclude
    #     fields = self._meta.fields
    #     opts = self.instance._meta
    #
    #     print(self.instance)
    #     print(cleaned_data)
    #     print(fields)
    #     print('opts')
    #     print(type(opts))
    #     print('opts')
    #     for f in chain(opts.many_to_many, opts.private_fields):
    #         if not hasattr(f, 'save_form_data'):
    #             continue
    #         if fields and f.name not in fields:
    #             continue
    #         if exclude and f.name in exclude:
    #             continue
    #         if f.name in cleaned_data:
    #             #print(f.name)
    #             if f.name == 'thema_lijst':
    #                 print('fix thema lijst')
    #                 pass
    #             else:
    #                 f.save_form_data(self.instance, cleaned_data[f.name])
    #
    #     print('---')
    #     #super()._save_m2m()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User  # non-swappable User model here.
        #exclude = ("username", )
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User  # non-swappable User model here.
        exclude = []


VoorwaardeFormSet = forms.inlineformset_factory(
    Regeling,
    Voorwaarde,
    form=RegelingModelForm,
    extra=1
)
ContactNaarRegelingFormSet = forms.inlineformset_factory(
    Regeling,
    ContactNaarRegeling,
    form=RegelingModelForm,
    extra=1
)
ThemaFormSet = forms.inlineformset_factory(
    Regeling,
    Regeling.themas.through,
    form=RegelingModelForm,
    extra=1,
)

class ProfielNaarThemaForm(forms.ModelForm):
    testveld = forms.CharField(label='test')

    class Meta:
        model = ProfielNaarThema
        exclude = []


ProfielThemaFormSet = forms.inlineformset_factory(
    Profiel,
    ProfielNaarThema,
    exclude=['volgorde', 'rol', ],
    # widgets={
    #    'thema': widgets.RadioSelect(attrs={'class': 'test'})
    # },
    form=ProfielNaarThemaForm,
    extra=0,
)


class BaseChildrenFormset(BaseInlineFormSet):
    pass
    # def add_fields(self, form, index):
    #     super().add_fields(form, index)
    #
    #     form.themas = ProfielThemaFormSet(
    #         instance=form.instance,
    #         data=form.data if form.is_bound else None,
    #         files=form.files if form.is_bound else None,
    #         prefix='thema-%s-%s' % (
    #             form.prefix,
    #             ProfielThemaFormSet.get_default_prefix()
    #         ),
    #     )
    #     qs = self.model._default_manager.get_queryset()
    #     print(form.instance)
    #     print(ProfielNaarThema.objects.filter(profiel=form.instance))
    #     print(self.fk)
    #     print(self.get_queryset())
    #     print(qs)
    #     print(qs.using(form.instance._state.db))
    #     count = Thema.objects.all().count()
    #     form.themas.max_num = count
    #     form.themas.min_num = count

    # def is_valid(self):
    #
    #     result = super().is_valid()
    #
    #     if self.is_bound:
    #         # look at any nested formsets, as well
    #         for form in self.forms:
    #             result = result and form.thema.is_valid()
    #
    #     return result
    #
    # def save(self, commit=True):
    #
    #     result = super().save(commit=commit)
    #
    #     for form in self:
    #         form.themas.save(commit=commit)
    #
    #     return result


UserFormSet = forms.inlineformset_factory(
    User,
    Profiel,
    fields=(
        'pasfoto',
        'voornaam',
        'tussenvoegsel',
        'achternaam',
        'functie',
        'email',
        'telefoonnummer',
        # 'organisatie_lijst',
        'thema_lijst',
    ),
    #formset=BaseChildrenFormset,
    widgets={
        'thema_lijst': widgets.CheckboxSelectMultiple(attrs={'class': 'choices inlineformset-checkbox'}),
    },

    form=ProfielModelForm,

)
