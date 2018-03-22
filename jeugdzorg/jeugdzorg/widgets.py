from django.forms.widgets import *


class ProfielCheckboxSelectMultiple(CheckboxSelectMultiple):
    option_template_name = 'form/checkbox_option.html'
    template_name = 'form/checkbox_list.html'


class ProfielCheckboxSelectMultipleGebied(CheckboxSelectMultiple):
    option_template_name = 'form/checkbox_option.html'
    template_name = 'form/checkbox_list_gebied.html'
