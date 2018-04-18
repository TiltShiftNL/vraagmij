from django.core.management.base import BaseCommand, CommandError
from jeugdzorg.cron import print_variables, update_regeling_bron_job
from jeugdzorg.utils import *
from django.core.cache import cache


class Command(BaseCommand):
    name = 'update_regeling_bron'
    help = 'update_regeling_bron'

    def handle(self, *args, **options):

        if get_container_id() != cache.get(get_cronjob_worker_cache_key()):
            raise CommandError("You're not the worker!")

        update_regeling_bron_job()
