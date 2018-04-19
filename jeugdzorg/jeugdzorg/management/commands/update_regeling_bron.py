from django.core.management.base import BaseCommand, CommandError
from jeugdzorg.cron import print_variables, update_regeling_bron_job
from jeugdzorg.utils import *
from django.core.cache import cache
from django.utils import timezone
import datetime
from dateutil.tz import tzlocal


class Command(BaseCommand):
    name = 'update_regeling_bron'
    help = 'update_regeling_bron'

    def handle(self, *args, **options):
        now = datetime.datetime.now(tzlocal())
        if get_container_id() != cache.get(get_cronjob_worker_cache_key()):
            raise CommandError("You're not the worker!")
        print('%s: %s' % (now.strftime('%Y-%m-%d %H:%M'), self.__module__.split('.')[-1]))
        update_regeling_bron_job()
