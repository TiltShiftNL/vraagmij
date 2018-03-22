from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from django.contrib.sites.models import Site
from jeugdzorg.models import Instelling


class Command(BaseCommand):
    help = 'Create crontabs from code'

    def handle(self, *args, **options):
        update_mail_frequentie = '0 0 1 * *'
        try:
            site = Site.objects.get_current()
            instelling = Instelling.objects.get(site=site)
            f = instelling.update_mail_frequentie
            len(f.strip().split(' '))
            if len(f.strip().split(' ')) == 5:
                update_mail_frequentie = f.strip()
        except:
            pass

        with open('/etc/cron.d/crontab', 'a') as crontabfile:
            crontabfile.write('*/20 * * * * root . /root/project_env.sh; /usr/local/bin/update_regelingen.sh >> /var/log/cron.log 2>&1\n')
            crontabfile.write('*/20 * * * * root . /root/project_env.sh; /usr/local/bin/check_user_activity.sh >> /var/log/cron.log 2>&1\n')
            crontabfile.write('%s root . /root/project_env.sh; /usr/local/bin/send_update_mail.sh >> /var/log/cron.log 2>&1\n' % update_mail_frequentie)
            crontabfile.write('\n')
