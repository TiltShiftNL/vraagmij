from jeugdzorg.models import CronjobState
from jeugdzorg.utils import *
import time
from django.utils import timezone


def get_container_int():
    return round(int('0x%s' % [l.strip() for l in open('/etc/hosts', 'r')][-1].split('\t')[1], 0) / 1000000000)


def get_container_id():
    return [l.strip() for l in open('/etc/hosts', 'r')][-1].split('\t')[1]


def get_cronjob_worker_cache_key():
    return 'cronjob_worker_id'


def cronjob_container_check(name):
    now = timezone.now()
    now_str = now.strftime('%Y-%m-%d %H:%M')
    container_int = (float(get_container_int()) / 1000)
    time.sleep(container_int)
    cronjob = CronjobState.objects.filter(naam_command=name)
    if not cronjob:
        cronjob = CronjobState(naam_command=name, datumtijd_string=now_str)
        cronjob.save()
    else:
        if cronjob.filter(datumtijd_string=now_str):
            print('%s - %s: SKIP' % (name, now_str))
            return False
        else:
            cronjob[0].datumtijd_string = now_str
            cronjob[0].save()
    print('%s - %s: DOING' % (name, now_str))
    return True