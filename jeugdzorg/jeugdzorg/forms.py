from django import forms
from django.forms import widgets
from .models import *
from django.core.management import call_command


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


# class UserCreationForm(forms.ModelForm):
#     class Meta:
#         model = User  # non-swappable User model here.
#         exclude = []
#
#
# class UserChangeForm(forms.ModelForm):
#     class Meta:
#         model = User  # non-swappable User model here.
#         exclude = []


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
    fields=('thema',),
    form=RegelingModelForm,
    extra=1,

)
