from django.contrib.auth.management.commands import createsuperuser
from django.core.management import CommandError
from django.db import connection
from django.contrib.auth import (
    authenticate, get_user_model, password_validation,
)
from django.core.management.base import BaseCommand
from jeugdzorg.models import EventItem
UserModel = get_user_model()
from django.utils import timezone
from jeugdzorg.models import *
from django.conf import settings
import sys
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'rebuild index'

    def handle(self, *args, **options):
        indexes = settings.SEARCH_MODELS
        for index in indexes:
            cls = getattr(sys.modules[__name__], index)
            if hasattr(cls, 'search'):
                # print(cls)
                r = cls.search.all()
                s = None
                try:
                    s = render_to_string('search/search_%s.html' % index.lower(), {'object_list': r})
                    # print(s)

                except:
                    print(index.lower())
                if s:
                    # print(s)
                    text_file = open('/opt/app/jeugdzorg/search_files/search_%s.html' % index.lower(), "w+")
                    text_file.write(s)
                    text_file.close()


