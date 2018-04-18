from django.core.management.base import BaseCommand
from jeugdzorg.utils import *
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Sets container id for worker cache key'

    def handle(self, *args, **options):
        cache.set(get_cronjob_worker_cache_key(), get_conatainer_id(), None)
