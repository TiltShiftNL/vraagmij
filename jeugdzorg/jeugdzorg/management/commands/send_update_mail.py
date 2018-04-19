from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from jeugdzorg.models import *
from django.template import engines
from django.utils import timezone
import dateutil.relativedelta
from django.urls import reverse
from sendgrid.helpers.mail import *
from django.conf import settings
import sendgrid
from jeugdzorg.context_processors import app_settings
import sys, os
import base64
from jeugdzorg.utils import *
from jeugdzorg.statics import *
from django.core.cache import cache
import datetime
from dateutil.tz import tzlocal


def build_logo():
    """Build attachment mock."""
    # attachment = Attachment()
    # attachment.content = "BwdW"
    # attachment.type = "image/png"
    # attachment.filename = "logo.png"
    # attachment.disposition = "inline"
    # attachment.content_id = "image-logo"
    # return attachment

    # Where it was uploaded Path.
    file_path = os.path.join(settings.STATIC_ROOT, 'images/ico_andreas.png')

    with open(file_path, 'rb') as f:
        data = f.read()

    # Encode contents of file as Base 64
    encoded = base64.b64encode(data).decode()

    """Build attachment"""
    attachment = Attachment()
    attachment.content = encoded
    attachment.type = "image/png"
    attachment.filename = "logo.png"
    # attachment.disposition = "attachment"
    attachment.disposition = "inline"
    attachment.content_id = "gfgrtdtrdk9769875786thgjhbj"

    return attachment


class Command(BaseCommand):
    help = 'Send update mail'

    def handle(self, *args, **options):
        now = datetime.datetime.now(tzlocal())
        if get_container_id() != cache.get(get_cronjob_worker_cache_key()):
            raise CommandError("You're not the worker!")
        print('%s: %s' % (now.strftime('%Y-%m-%d %H:%M'), self.__module__.split('.')[-1]))
        site = Site.objects.get_current()
        if site.instelling:
            sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
            now = now + dateutil.relativedelta.relativedelta(months=-1)
            regeling_nieuw = Regeling.objects.filter(**{
                'datum_gecreeerd__gt': now
            })
            gebruikers_nieuw = User.objects.filter(**{
                'date_joined__gt': now,
            }).exclude(profiel=None)
            regeling_gewijzigd = Regeling.objects.filter(**{
                'datum_gecreeerd__lte': now,
                'datum_opgeslagen__gt': now,
            })

            regeling_nieuw_str = [[r.titel, 'https://%s%s' % (site.domain, reverse('detail_regeling', kwargs={'pk': r.id}))] for r in regeling_nieuw]
            regeling_gewijzigd_str = [[r.titel, 'https://%s%s' % (site.domain, reverse('detail_regeling', kwargs={'pk': r.id}))] for r in regeling_gewijzigd]
            gebruikers_nieuw_str = [[r.profiel.naam_volledig, 'https://%s%s' % (site.domain, reverse('detail_contact', kwargs={'pk': r.id}))] for r in gebruikers_nieuw]

            django_engine = engines['django']
            maand = maanden[int(now.strftime('%-m'))-1]
            subject = 'VraagMij - updates maand %s' % maand
            data = {
                'regeling_nieuw': regeling_nieuw_str,
                'regeling_gewijzigd': regeling_gewijzigd_str,
                'gebruikers_nieuw': gebruikers_nieuw_str,
                'subject': subject,
            }

            for u in User.objects.exclude(profiel=None):
                if u.profiel.hou_me_op_de_hoogte_mail:
                    o = {
                        'naam': u.profiel.naam_volledig,
                        'profiel': u.profiel,
                    }
                    o.update(data)
                    o.update(app_settings())
                    template = django_engine.from_string(site.instelling.update_mail_content)
                    template_html = django_engine.from_string(site.instelling.update_mail_content_html)

                    body_html = template_html.render(o)
                    body = template.render(o)

                    mail_settings = MailSettings()
                    mail = Mail(
                        Email('noreply@%s' % site.domain),
                        subject,
                        Email(u.email),
                        Content("text/plain", body)
                    )
                    mail.mail_settings = mail_settings
                    mail.add_content(Content("text/html", body_html))
                    #
                    # mail.add_attachment(build_logo())
                    # h1 = Header('Content-Id', '<gfgrtdtrdk9769875786thgjhbj>')
                    # mail.add_header(h1)


                    if settings.ENV != 'develop':
                        sg.client.mail.send.post(request_body=mail.get())
                        # print('Send mail to: %s' % u.email)
                    else:
                        print(body_html)

