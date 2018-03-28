from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from django.contrib.sites.models import Site
from jeugdzorg.models import Instelling


class Command(BaseCommand):
    help = 'Create crontabs from code'

    def handle(self, *args, **options):
        job_base_1 = 'root . /root/project_env.sh; /usr/local/bin/'
        job_base_2 = '.sh >> /var/log/cron.log 2>&1\n'
        jobs = [
            'update_regelingen',
            'check_user_activity',
            'send_update_mail',
            'gebruiker_email_verificatie',
        ]
        try:
            site = Site.objects.get_current()
            instelling = Instelling.objects.get(site=site)
            with open('/etc/cron.d/crontab', 'w') as crontabfile:
                for j in jobs:
                    crontabfile.write(
                        '%s %s%s%s' % (
                            getattr(instelling, '%s_frequentie' % j, '0 0 0 1 *'),
                            job_base_1,
                            j,
                            job_base_2,
                        ))
                crontabfile.write('\n')
            print('new crontabs created')
        except Exception as e:
            print('create crontabs: %s (%s)' % (e.message, type(e)))



        # update_mail_frequentie = '0 0 0 1 *'
        # gebruiker_email_verificatie_frequentie = '0 0 0 1 *'
        # update_regelingen_frequentie = '0 0 0 1 *'
        # check_user_activity_frequentie = '0 0 0 1 *'
        # try:
        #     site = Site.objects.get_current()
        #     instelling = Instelling.objects.get(site=site)
        #     umf = instelling.update_mail_frequentie
        #     gevf = instelling.gebruiker_email_verificatie_frequentie
        #     urf = instelling.update_regelingen_frequentie
        #     cuaf = instelling.check_user_activity_frequentie
        #     if len(umf.strip().split(' ')) == 5:
        #         update_mail_frequentie = umf.strip()
        #     if len(gevf.strip().split(' ')) == 5:
        #         gebruiker_email_verificatie_frequentie = gevf.strip()
        #     if len(urf.strip().split(' ')) == 5:
        #         update_regelingen_frequentie = urf.strip()
        #     if len(cuaf.strip().split(' ')) == 5:
        #         check_user_activity_frequentie = cuaf.strip()
        # except:
        #     pass
        #
        # with open('/etc/cron.d/crontab', 'a') as crontabfile:
        #     crontabfile.write('%s root . /root/project_env.sh; /usr/local/bin/update_regelingen.sh >> /var/log/cron.log 2>&1\n')
        #     crontabfile.write('%s root . /root/project_env.sh; /usr/local/bin/check_user_activity.sh >> /var/log/cron.log 2>&1\n')
        #     crontabfile.write('%s root . /root/project_env.sh; /usr/local/bin/send_update_mail.sh >> /var/log/cron.log 2>&1\n' % update_mail_frequentie)
        #     crontabfile.write('%s root . /root/project_env.sh; /usr/local/bin/gebruiker_email_verificatie.sh >> /var/log/cron.log 2>&1\n' % gebruiker_email_verificatie_frequentie)
        #     crontabfile.write('\n')
