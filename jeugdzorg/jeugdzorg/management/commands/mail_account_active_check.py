from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.db import connection
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.urls import reverse
from django.core.management.base import BaseCommand
from jeugdzorg.models import EventItem
UserModel = get_user_model()
from django.utils import timezone
from django.contrib.sites.models import Site
from jeugdzorg.models import Instelling
from django.conf import settings
from sendgrid.helpers.mail import *
import sendgrid
import json
from jeugdzorg.statics import *
from jeugdzorg.utils import *
import dateutil.relativedelta
from jeugdzorg.context_processors import app_settings
from django.template.loader import render_to_string
from django.template import engines


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
    help = 'mail_account_active_check'
    name = 'mail_account_active_check'

    def handle(self, *args, **options):
        if get_container_id() != cache.get(get_cronjob_worker_cache_key()):
            raise CommandError("You're not the worker!")

        site = Site.objects.get_current()
        if site.instelling:
            sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
            now = timezone.now()

            subject = 'VraagMij - Is je profiel up-to-date?'

            for u in get_users():
                if u.profiel.hou_me_op_de_hoogte_mail:
                    o = {
                        'naam': u.profiel.naam_volledig,
                        'profiel': u.profiel,
                    }
                    o.update(app_settings())

                    body = render_to_string('email/mail_account_active_check.txt',  o)
                    body_html = render_to_string('email/mail_account_active_check.html', o)

                    mail = Mail(
                        Email('noreply@%s' % site.domain),
                        subject,
                        Email(u.email),
                        Content("text/plain", body)
                    )
                    mail.add_content(Content("text/html", body_html))

                    if settings.ENV != 'develop':
                        sg.client.mail.send.post(request_body=mail.get())
                    else:
                        print(body)
                    print('Send mail to: %s' % u.email)


