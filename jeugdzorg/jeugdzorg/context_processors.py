# -*- coding: utf-8 -*-
from django.conf import settings


def app_settings(request):

    return {
        'ENV': settings.ENV,
        'BUILD_NUMBER': settings.BUILD_NUMBER,
    }
