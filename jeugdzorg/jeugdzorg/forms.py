from django import forms
from .models import *


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


def handle_uploaded_file(f):
    with open('/opt/file_upload/jeugdzorg.json', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


class RegelingModelForm(forms.ModelForm):
    class Meta:
        model = Regeling
        exclude = []


VoorwaardeFormSet = forms.inlineformset_factory(Regeling, Voorwaarde,
                                            form=RegelingModelForm, extra=1)