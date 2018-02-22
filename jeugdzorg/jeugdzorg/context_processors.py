# -*- coding: utf-8 -*-
from django.conf import settings


def app_settings(request):

    return {
        'ENV': settings.ENV,
        'SOURCE_COMMIT': settings.SOURCE_COMMIT,
        'UWSGI_TEST': request.environ.get('UWSGI_TEST'),
    }
