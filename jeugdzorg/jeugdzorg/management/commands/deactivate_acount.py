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
from django.contrib.sites.models import Site
from jeugdzorg.models import Instelling


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
    help = 'Deactivate account'
    treshold = 60 * 60 * 24 * 30 * 6

    def handle(self, *args, **options):
        now = int(timezone.now().timestamp())
        for u in get_users():
            delete = False
            exist = EventItem.objects.filter(**{
                'user': u,
                # 'url__endswith': '/profiel/bewerken',
                # 'name': 'load.page',
            }).order_by('-timestamp')
            if exist:
                if u.profiel.seconden_niet_gebruikt > self.treshold:
                    delete = True

            login_div = now - int(u.last_login.timestamp())
            if login_div > self.treshold:
                delete = True

            if delete:
                u.is_active = False
                u.profiel.save()



