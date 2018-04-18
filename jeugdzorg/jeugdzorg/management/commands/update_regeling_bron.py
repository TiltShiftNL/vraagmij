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

        if get_container_id() != cache.get(get_cronjob_worker_cache_key()):
            raise CommandError("You're not the worker!")

        update_regeling_bron_job()
