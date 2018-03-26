from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from django.contrib.sites.models import Site
from jeugdzorg.models import *
from django.shortcuts import render
from django.template.loader import render_to_string
from django.template import engines
from django.utils import timezone
from datetime import timedelta
import dateutil.relativedelta
from django.urls import reverse
from sendgrid.helpers.mail import *
from django.conf import settings
import sendgrid
from jeugdzorg.context_processors import app_settings


class Command(BaseCommand):
    help = 'Send update mail'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        if site.instelling:


            now = timezone.now()
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
            data = {
                'regeling_nieuw': regeling_nieuw_str,
                'regeling_gewijzigd': regeling_gewijzigd_str,
                'gebruikers_nieuw': gebruikers_nieuw_str,
            }

            for u in User.objects.exclude(profiel=None):
                if u.profiel.hou_me_op_de_hoogte_mail:
                    o = {'naam': u.profiel.naam_volledig}
                    o.update(data)
                    o.update(app_settings())
                    template = django_engine.from_string(site.instelling.update_mail_content)
                    body = template.render(o)
                    subject = 'VraagMij - updates maand %s' % now.strftime('%B')
                    mail = Mail(
                        Email('noreply@%s' % site.domain),
                        subject,
                        Email(u.email),
                        Content("text/plain", body)
                    )
                    # print(body)

                    if settings.ENV != 'develop':
                        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
                        sg.client.mail.send.post(request_body=mail.get())
                    print('Send mail to: %s' % u.profiel.naam_volledig)

            sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
            url = "suppression/bounces?start_time={start_time}&end_time={end_time}".format(**{
                'start_time': 1521557086,
                'end_time': 1521816286,
            })
            response = sg.client._(url).get()
            print(response.status_code)
            print(response.body)
            print(response.headers)

