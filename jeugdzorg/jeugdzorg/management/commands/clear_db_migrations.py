from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.core.management import CommandError
from django.db import connection


def clear_migrations():
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM public.django_migrations")


class Command(BaseCommand):
    help = 'clear_db_migrations'

    def handle(self, *args, **options):
        clear_migrations()
