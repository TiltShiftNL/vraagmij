from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from jeugdzorg.cron import print_variables


class Command(createsuperuser.Command):
    help = 'Crate a superuser, and allow password to be provided'

    def handle(self, *args, **options):
        print_variables()
