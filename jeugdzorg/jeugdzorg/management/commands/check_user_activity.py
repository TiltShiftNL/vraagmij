from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.db import connection
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.core.management.base import BaseCommand
from jeugdzorg.models import EventItem
UserModel = get_user_model()
from django.utils import timezone


def get_users():
    """Given an email, return matching user(s) who should receive a reset.

    This allows subclasses to more easily customize the default policies
    that prevent inactive users and users with unusable passwords from
    resetting their password.
    """
    active_users = UserModel._default_manager.filter(**{
        'is_active': True,
    })
    return (u for u in active_users if u.has_usable_password())


class Command(BaseCommand):
    help = 'check user activity'

    def handle(self, *args, **options):
        print('START JOB check user activity')
        # day = 60 * 60 * 24
        treshold = 60 * 60 * 24 * 30 * 6
        for u in get_users():
            exist = EventItem.objects.filter(**{
                'user': u,
                'url__endswith': '/profiel/bewerken',
                'name': 'load.page',
            }).order_by('-timestamp')
            if exist:
                div = int(timezone.now().timestamp()) - int(exist[0].timestamp)/1000
                div = round(div)
                # print(div)
                # div = div - (div % 60)
                # print(div)
                # div = div / 60
                # print(round(div))
                u.profiel.seconden_niet_gebruikt = div
                u.profiel.save()
                if div > treshold:
                    print('TO OLD')

