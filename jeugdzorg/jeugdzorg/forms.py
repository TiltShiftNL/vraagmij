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
from .widgets import ProfielCheckboxSelectMultiple
from django.forms.utils import ErrorList


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


class ProfielModelForm(forms.ModelForm):
    custom_m2m = (
        ('thema_lijst', 'thema'),
        ('regeling_lijst', 'regeling'),
        ('organisatie_lijst', 'organisatie'),
    )

    class Meta:
        model = Profiel
        exclude = []

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        for f in self.custom_m2m:
            self.fields[f[0]].required = False

    def save(self, commit=True):
        print('save')
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m
        def save_m2m():
            # todo normal m2m not saved
            #old_save_m2m()

            for cm2m in self.custom_m2m:

                getattr(instance, cm2m[0]).clear()

                for obj in self.cleaned_data[cm2m[0]]:
                    data = dict(profiel=instance)
                    data[cm2m[1]] = obj
                    profielrel = getattr(instance, cm2m[0]).through(**data)
                    profielrel.save()
        self.save_m2m = save_m2m
        if commit:
            instance.save()
            self.save_m2m()
        return instance


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
        'zichtbaar',
        'pasfoto',
        'voornaam',
        'tussenvoegsel',
        'achternaam',
        'functie',
        'vaardigheden',
        'email',
        'telefoonnummer',
        'organisatie_lijst',
        'regeling_lijst',
        'thema_lijst',
    ),
    #formset=BaseChildrenFormset,
    widgets={
        'regeling_lijst': ProfielCheckboxSelectMultiple(attrs={'class': 'choices'}),
        'organisatie_lijst': ProfielCheckboxSelectMultiple(attrs={'class': 'choices'}),
        'thema_lijst': ProfielCheckboxSelectMultiple(attrs={'class': 'choices'}),
    },

    form=ProfielModelForm,

)
