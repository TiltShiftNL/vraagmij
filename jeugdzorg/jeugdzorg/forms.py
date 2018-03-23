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
from .widgets import *
from .fields import *
from django.forms.utils import ErrorList
from itertools import groupby
from django.urls import reverse, reverse_lazy
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import SetPasswordForm

UserModel = get_user_model()


def file_size(value): # add this to some file where you can import it from
    limit = 5 * 1024 * 1024
    if value.size > limit:
        print('max')
        raise ValidationError('De bestandsgrootte van de foto is meer dan 5M.', code='invalid')


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

        body = loader.render_to_string(email_template_name, context)
        print(body)

        if settings.ENV != 'develop':
            mail = Mail()
            print(to_email)
            try:
                context.update({
                    'profiel': User.objects.get(email=to_email).profiel
                })
            except:
                pass
            subject = loader.render_to_string(subject_template_name, context)
            subject = "".join(subject.splitlines())
            #body = 'body'#loader.render_to_string(email_template_name, context)
            html_body = ''
            if html_email_template_name is not None:
                html_body = loader.render_to_string(html_email_template_name, context)

            sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
            # from_email = Email(from_email)
            # to_email = Email(to_email)

            mail.from_email = Email("noreply@fixxx7.amsterdam.nl")
            mail.reply_to = Email(to_email)
            mail.subject = subject

            #mail.add_content(Content("text/plain", body))
            #mail.add_content(Content("text/html", html_body))

            mail = Mail(Email('noreply@fixxx7.amsterdam.nl'), subject, Email(to_email), Content("text/plain", body))
            # print(response.status_code)
            # print(response.body)
            # print(response.headers)

            sg.client.mail.send.post(request_body=mail.get())


# class SetPasswordNewForm(SetPasswordForm):
#     def save(self, commit=True):
#         messages.add_message(self.request, messages.INFO, "Je wachtwoord is ingesteld.")
#         return super().save(commit)


class RegelingModelForm(forms.ModelForm):
    thema_lijst = forms.ModelMultipleChoiceField(
        required=False,
        widget=ProfielCheckboxSelectMultiple(attrs={'class': 'choices'}),
        queryset=Thema.objects.all(),
    )
    custom_m2m = (
        ('thema_lijst', 'thema'),
    )

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

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if commit:
            for thema in cleaned_data.get('thema_lijst'):
                print(thema)
        return super().save(commit)


class ProfielModelForm(forms.ModelForm):
    #pasfoto = forms.ImageField(required=False, validators=[file_size])
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

        self.fields['gebied_lijst'].required = False
        gebied_lijst_choices = []
        for k, gl in groupby(Gebied.objects.all().order_by('stadsdeel'), lambda x: x.stadsdeel):
            gebied_lijst_choices.append([k, [[g.id, g.naam] for g in gl]])
        self.fields['gebied_lijst'].choices = gebied_lijst_choices

        for f in self.custom_m2m:
            self.fields[f[0]].required = False

        self.fields['telefoonnummer'].widget = widgets.TextInput(attrs={'placeholder': '+31612345678'})
        self.fields['telefoonnummer_2'].widget = widgets.TextInput(attrs={'placeholder': '+31612345678'})

    def clean_pasfoto(self):
        value = self.cleaned_data.get('pasfoto')
        limit = 5 * 1024 * 1024
        if value and value.size > limit:
            raise ValidationError('De bestandsgrootte van de pasfoto is meer dan 5M.', code='invalid')
        return value

    def _save_m2m(self):
        """
        Save the many-to-many fields and generic relations for this form.
        """
        cleaned_data = self.cleaned_data
        exclude = self._meta.exclude
        fields = self._meta.fields
        opts = self.instance._meta
        # Note that for historical reasons we want to include also
        # private_fields here. (GenericRelation was previously a fake
        # m2m field).
        for f in chain(opts.many_to_many, opts.private_fields):
            if not hasattr(f, 'save_form_data'):
                continue
            if fields and f.name not in fields:
                continue
            if f.name in [c[0] for c in self.custom_m2m]:
                continue
            if exclude and f.name in exclude:
                continue
            if f.name in cleaned_data:
                f.save_form_data(self.instance, cleaned_data[f.name])

    def save(self, commit=True):
        instance = forms.ModelForm.save(self, False)
        old_save_m2m = self.save_m2m

        def save_m2m():
            # todo normal m2m not saved
            old_save_m2m()

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


class VoorwaardeModelForm(forms.ModelForm):
    class Meta:
        model = Regeling
        exclude = []


VoorwaardeFormSet = forms.inlineformset_factory(
    Regeling,
    Voorwaarde,
    form=VoorwaardeModelForm,
    extra=1
)
ContactNaarRegelingFormSet = forms.inlineformset_factory(
    Regeling,
    ContactNaarRegeling,
    form=RegelingModelForm,
    extra=1
)


class ThemaModelForm(forms.ModelForm):
    class Meta:
        model = Thema
        exclude = []

    def save(self, commit=True):
        return super().save(commit)


ThemaFormSet = forms.inlineformset_factory(
    Regeling,
    Regeling.themas.through,
    form=ThemaModelForm,
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
        'telefoonnummer_2',
        'organisatie_lijst',
        'regeling_lijst',
        'thema_lijst',
        'gebied_lijst',
    ),
    #formset=BaseChildrenFormset,
    widgets={
        'regeling_lijst': ProfielCheckboxSelectMultiple(attrs={'class': 'choices choices-full'}),
        'organisatie_lijst': ProfielCheckboxSelectMultiple(attrs={'class': 'choices'}),
        'thema_lijst': ProfielCheckboxSelectMultiple(attrs={'class': 'choices'}),
        'gebied_lijst': ProfielCheckboxSelectMultipleGebied(
            attrs={
                'class': 'choices',
            }
        )
    },

    form=ProfielModelForm,

)
