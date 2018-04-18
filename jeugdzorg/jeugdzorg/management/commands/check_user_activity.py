from django.core.management import CommandError
from django.contrib.auth import (get_user_model, )
from django.core.management.base import BaseCommand
from jeugdzorg.models import EventItem
UserModel = get_user_model()
from django.utils import timezone
from jeugdzorg.utils import *
from django.core.cache import cache


def get_users():
    """Given an email, return matching user(s) who should receive a reset.

    This allows subclasses to more easily customize the default policies
    that prevent inactive users and users with unusable passwords from
    resetting their password.
    """
    active_users = UserModel._default_manager.filter(**{
        'is_active': True,
    }).exclude(profiel=None)
    return (u for u in active_users if u.has_usable_password())


class Command(BaseCommand):
    help = 'check user activity'

    def handle(self, *args, **options):
        if get_container_id() != cache.get(get_cronjob_worker_cache_key()):
            raise CommandError("You're not the worker!")

        for u in get_users():
            exist = EventItem.objects.filter(**{
                'user': u,
                # 'url__endswith': '/profiel/bewerken',
                # 'name': 'load.page',
            }).order_by('-timestamp')
            if exist:
                div = int(timezone.now().timestamp()) - int(exist[0].timestamp)/1000
                div = round(div)
                u.profiel.seconden_niet_gebruikt = div
                u.profiel.save()

