from django.contrib.auth.models import Group


def auth_test(user, group_name):
    group = []
    try:
        group = Group.objects.get(name=group_name)
    except:
        pass
    return (group in user.groups.all()) or user.is_superuser
