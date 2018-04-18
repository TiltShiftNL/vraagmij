from django.core.management.base import BaseCommand
from jeugdzorg.utils import *
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Sets container id for worker cache key'

    def handle(self, *args, **options):
        print('set_cronjob_worker: %s' % get_container_id())
        cache.set(get_cronjob_worker_cache_key(), get_container_id(), None)
