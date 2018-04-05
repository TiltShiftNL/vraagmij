from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from jeugdzorg.cron import print_variables, update_regeling_bron_job
from jeugdzorg.models import CronjobState
from jeugdzorg.utils import *
import time
from django.utils import timezone
from datetime import datetime

current_milli_time = lambda: int(round(time.time() * 1000))

class Command(BaseCommand):
    name = 'update_regeling_bron'
    help = 'update_regeling_bron'

    def handle(self, *args, **options):
        ms = current_milli_time()
        now = timezone.now()
        now = timezone.datetime(now.year, now.month, now.day, now.hour, now.minute)
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        print(now_str)
        container_int = (float(get_container_int()) / 1000)
        print(container_int)
        time.sleep(container_int)
        print(current_milli_time() - ms)

        cronjob = CronjobState.objects.filter(naam_command=self.name)
        if not cronjob:
            cronjob = CronjobState(naam_command=self.name, datumtijd_command=now, datumtijd_string=now_str)
            cronjob.save()
        else:
            print(cronjob)
            print(cronjob.filter(datetime_string=now_str))
            if cronjob.filter(datumtijd_string=now_str):
                print('update_regeling_bron: SKIP')
                return
            else:
                print('update datetime')
                cronjob[0].datumtijd_command = now
                cronjob[0].datumtijd_string = now_str
                cronjob[0].save()

        print('update_regeling_bron: DOING')
        update_regeling_bron_job()
