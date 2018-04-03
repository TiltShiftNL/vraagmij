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
import sys, os
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'rebuild index'

    def handle(self, *args, **options):
        indexes = settings.SEARCH_MODELS
        dir = '/opt/app/jeugdzorg/search_files/'
        if not os.path.exists(dir):
            os.makedirs(dir)
        text_file = open('%ssearch.json' % dir, "w+")
        text_file.write('"data":[')
        text_file.close()
        text_file = open('%ssearch.html' % dir, "w+")
        text_file.write('')
        text_file.close()

        for index in indexes:
            cls = getattr(sys.modules[__name__], index)
            if hasattr(cls, 'search'):
                r = cls.search.all()
                s, sj = None, None
                try:
                    sj = render_to_string('search/search_%s.json' % index.lower(), {'object_list': r})
                    s = render_to_string('search/search_%s.html' % index.lower(), {'object_list': r})
                except:
                    print(index.lower())

                if s:
                    text_file = open('%ssearch.html' % dir, "a")
                    text_file.write('<div class="zoeken-paneel %s-lijst">%s</div>' % (index, s))
                    text_file.close()
                    text_file = open('%ssearch_%s.html' % (dir, index.lower()), "w+")
                    text_file.write(s)
                    text_file.close()
                if sj:
                    text_file = open('%ssearch.json' % dir, "a")
                    text_file.write(sj)
                    text_file.close()
        text_file = open('%ssearch.json' % dir, "a")
        text_file.write(']')
        text_file.close()

