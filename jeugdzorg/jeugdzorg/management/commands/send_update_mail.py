from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Send update mail'

    def handle(self, *args, **options):
        print('Send update mail')
        site = Site.objects.get_current()
        print(site)
