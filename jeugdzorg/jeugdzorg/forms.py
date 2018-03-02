from django import forms
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
        exclude = []


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

DoelFormSet = forms.inlineformset_factory(
    Regeling,
    Regeling.doelen.through,
    fields=('doel', ),
    form=RegelingModelForm,
    extra=1,

)


