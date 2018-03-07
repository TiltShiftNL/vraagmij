from django import forms
from django.forms import widgets
from .models import *
from django.core.management import call_command
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.forms import AuthenticationForm
from django.forms.models import BaseInlineFormSet


class UploadJeugdzorgFixtureFileForm(forms.Form):
    file = forms.FileField(
        label='Upload jeugdzorg.json'
    )


def handle_uploaded_file(f):
    with open('/opt/file_upload/jeugdzorg.json', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    call_command('loaddata', '/opt/file_upload/jeugdzorg.json', app_label='jeugdzorg')


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

ProfielThemaFormSet = forms.inlineformset_factory(
    Profiel,
    ProfielNaarThema,
    exclude=['volgorde', 'rol', ],
    extra=1,
)


class BaseChildrenFormset(BaseInlineFormSet):

    def add_fields(self, form, index):
        super().add_fields(form, index)

        form.themas = ProfielThemaFormSet(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='thema-%s-%s' % (
                form.prefix,
                ProfielThemaFormSet.get_default_prefix()
            ),
        )

    def is_valid(self):

        result = super().is_valid()

        if self.is_bound:
            # look at any nested formsets, as well
            for form in self.forms:
                result = result and form.themas.is_valid()

        return result

    def save(self, commit=True):

        result = super().save(commit=commit)

        for form in self:
            form.themas.save(commit=commit)

        return result


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
        # 'thema_lijst',
    ),
    formset=BaseChildrenFormset,
    widgets={
        # 'thema_lijst': widgets.CheckboxSelectMultiple,
    },

    form=UserModelForm,

)
