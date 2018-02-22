from django import template
from django.contrib.auth.models import Group
from jeugdzorg.auth import auth_test
register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return auth_test(user, group_name)