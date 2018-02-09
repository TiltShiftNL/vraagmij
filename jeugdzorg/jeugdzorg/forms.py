from django import forms
from .models import *


class RegelingModelForm(forms.ModelForm):
    class Meta:
        model = Regeling
        exclude = []


VoorwaardeFormSet = forms.inlineformset_factory(Regeling, Voorwaarde,
                                            form=RegelingModelForm, extra=1)