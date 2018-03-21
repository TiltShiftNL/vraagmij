from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError


class Command(BaseCommand):
    help = 'Create crontabs from code'

    def handle(self, *args, **options):
        with open('/etc/cron.d/crontab', 'a') as crontabfile:
            crontabfile.write('*/20 * * * * root . /root/project_env.sh; /usr/local/bin/update_regelingen.sh >> /var/log/cron.log 2>&1\n')
            crontabfile.write('*/20 * * * * root . /root/project_env.sh; /usr/local/bin/check_user_activity.sh >> /var/log/cron.log 2>&1\n')
            crontabfile.write('* * * * * root . /root/project_env.sh; /usr/local/bin/send_update_mail.sh >> /var/log/cron.log 2>&1\n')
            crontabfile.write('\n')
