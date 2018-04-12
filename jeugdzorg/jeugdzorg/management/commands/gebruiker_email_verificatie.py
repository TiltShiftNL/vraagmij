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
from django.conf import settings
import sendgrid
import json


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
        if not cronjob_container_check(self.__module__.split('.')[-1]):
            return


        start_time = 1514764800
        end_time = int(timezone.now().timestamp())
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        bounces_base_url = 'suppression/bounces'
        invalid_emails_base_url = 'suppression/invalid_emails'
        spam_reports_base_url = 'suppression/spam_reports'

        bounces = sg.client._(bounces_base_url.format(**{
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
            'invalid_emails': json.loads(invalid_emails.body),
            'spam_reports': json.loads(spam_reports.body),
        }
        for u in get_users():
            for k, v in results.items():
                if u.email in [r.get('email') for r in v]:
                    r = dict((r.get('email'), r) for r in v).get(u.email)
                    u.profiel.gebruiker_email_verificatie = k
                    u.profiel.gebruiker_email_verificatie_details = ','.join(['%s: %s' % (k, v) for k, v in r.items()
                                                                              if k != 'email'])
                    u.profiel.save()



