from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from jeugdzorg.cron import update_regeling_bron_job


class Command(createsuperuser.Command):
    help = 'Crate a superuser, and allow password to be provided'

    def handle(self, *args, **options):
        update_regeling_bron_job()
