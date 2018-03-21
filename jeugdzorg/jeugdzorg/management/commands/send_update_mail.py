from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError


class Command(BaseCommand):
    help = 'Send update mail'

    def handle(self, *args, **options):
        pass
