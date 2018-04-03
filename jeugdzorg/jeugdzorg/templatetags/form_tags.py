from django import template
from jeugdzorg.forms import GebruikerUitnodigenForm
register = template.Library()


@register.inclusion_tag('form/gebruiker_uitnodigen.html', takes_context=True)
def get_gebruiker_uitnodigen_form(context):
    return {
        'form': GebruikerUitnodigenForm()
    }