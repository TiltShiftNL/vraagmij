from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from jeugdzorg.cron import print_variables, update_regeling_bron_job
from jeugdzorg.models import CronjobState
from jeugdzorg.utils import *
import time
from django.utils import timezone
from datetime import datetime


def get_container_int():
    return round(int('0x%s' % [l.strip() for l in open('/etc/hosts', 'r')][-1].split('\t')[1], 0) / 5000000000)


def cronjob_container_check(name):
    now = timezone.now()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S')
    container_int = (float(get_container_int()) / 1000)
    time.sleep(container_int)
    cronjob = CronjobState.objects.filter(naam_command=name)
    if not cronjob:
        cronjob = CronjobState(naam_command=name, datumtijd_string=now_str)
        cronjob.save()
    else:
        if cronjob.filter(datumtijd_string=now_str):
            print('%s: SKIP' % name)
            return False
        else:
            cronjob[0].datumtijd_string = now_str
            cronjob[0].save()
    print('%s: DOING' % name)
    return True