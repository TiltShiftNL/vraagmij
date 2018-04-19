from django.contrib.auth import (get_user_model, )
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
import sendgrid
import json
from jeugdzorg.utils import *
from django.core.cache import cache
import datetime
from dateutil.tz import tzlocal

UserModel = get_user_model()


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
    help = 'gebruiker email verificatie'

    def handle(self, *args, **options):
        now = datetime.datetime.now(tzlocal())
        if get_container_id() != cache.get(get_cronjob_worker_cache_key()):
            raise CommandError("You're not the worker!")

        print('%s: %s' % (now.strftime('%Y-%m-%d %H:%M'), self.__module__.split('.')[-1]))

        start_time = 1514764800
        end_time = int(now.timestamp())
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        bounces_base_url = 'suppression/bounces'
        blocks_base_url = 'suppression/blocks'
        invalid_emails_base_url = 'suppression/invalid_emails'
        spam_reports_base_url = 'suppression/spam_reports'

        bounces = sg.client._(bounces_base_url.format(**{
            'start_time': start_time,
        })).get()
        blocks = sg.client._(blocks_base_url.format(**{
            'start_time': start_time,
        })).get()
        invalid_emails = sg.client._(invalid_emails_base_url.format(**{
            'start_time': start_time,
        })).get()
        spam_reports = sg.client._(spam_reports_base_url.format(**{
            'start_time': start_time,
        })).get()

        results = {
            'bounces': json.loads(bounces.body),
            'blocks': json.loads(blocks.body),
            'invalid_emails': json.loads(invalid_emails.body),
            'spam_reports': json.loads(spam_reports.body),
        }
        print(results)
        for u in get_users():
            for k, v in results.items():
                if u.email in [r.get('email') for r in v]:
                    r = dict((r.get('email'), r) for r in v).get(u.email)
                    u.profiel.gebruiker_email_verificatie = k
                    u.profiel.gebruiker_email_verificatie_details = ','.join(['%s: %s' % (k, v) for k, v in r.items()
                                                                              if k != 'email'])
                    u.profiel.save()



