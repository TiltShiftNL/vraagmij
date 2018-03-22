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


class Command(BaseCommand):
    help = 'Send update mail'

    def handle(self, *args, **options):
        site = Site.objects.get_current()
        if site.instelling:
            sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
            bullet = u"\u2022"
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

            regeling_nieuw_str = [[r.titel, '%s%s' % (site.domain, reverse('detail_regeling', kwargs={'pk': r.id}))] for r in regeling_nieuw]
            regeling_gewijzigd_str = [[r.titel, '%s%s' % (site.domain, reverse('detail_regeling', kwargs={'pk': r.id}))] for r in regeling_gewijzigd]
            gebruikers_nieuw_str = [[r.profiel.naam_volledig, '%s%s' % (site.domain, reverse('detail_contact', kwargs={'pk': r.id}))] for r in gebruikers_nieuw]

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
                    template = django_engine.from_string(site.instelling.update_mail_content)
                    body = template.render(o)
                    subject = 'VraagMij - updates maand %s' % now.strftime('%B')
                    mail = Mail(
                        Email('noreply@fixxx7.amsterdam.nl'),
                        subject,
                        Email(u.email),
                        Content("text/plain", body)
                    )
                    if not settings.DEBUG:
                        sg.client.mail.send.post(request_body=mail.get())
                    print('Send mail to: %s' % u.profiel.naam_volledig)

