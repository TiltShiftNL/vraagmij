from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from django.contrib.sites.models import Site
from jeugdzorg.models import Instelling
from django.utils import timezone


class Command(BaseCommand):
    help = 'Create crontabs from code'

    def handle(self, *args, **options):
        job_base_1 = 'root . /root/project_env.sh; /usr/local/bin/'
        job_base_2 = '.sh >> /var/log/cron.log 2>&1\n'
        jobs = [
            ('set_cronjob_worker', '@reboot', ),
            ('mail_account_active_check', '0 0 1 */6 *', ),
            ('update_regelingen', '0 0 0 1 *', ),
            ('check_user_activity', '0 0 0 1 *', ),
            ('send_update_mail', '0 0 0 1 *', ),
            ('gebruiker_email_verificatie', '0 0 0 1 *', ),
            ('create_crontabs', '*/5 * * * *', ),
        ]
        try:
            site = Site.objects.get_current()
            instelling = Instelling.objects.get(site=site)
            with open('/etc/cron.d/crontab', 'w') as crontabfile:
                for j in jobs:
                    f = getattr(instelling, '%s_frequentie' % j[0], j[1])
                    crontabfile.write(
                        '%s %s%s%s' % (
                            f,
                            job_base_1,
                            j[0],
                            job_base_2,
                        ))
                crontabfile.write('\n')
            print('new crontabs created')
        except Exception as e:
            print('create crontabs: %s (%s)' % (e.message, type(e)))