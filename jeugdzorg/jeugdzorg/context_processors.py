# -*- coding: utf-8 -*-
from django.conf import settings


def app_settings(request):
    print(request)
    return {
        'ENV': settings.ENV,
        'SOURCE_COMMIT': settings.SOURCE_COMMIT,
    }
