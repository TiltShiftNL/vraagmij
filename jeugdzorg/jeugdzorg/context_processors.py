# -*- coding: utf-8 -*-
from django.conf import settings
from jeugdzorg.models import *
from django.contrib.sites.models import Site


def app_settings(request=None):
    instelling = None

    try:
        site = Site.objects.get_current()
        instelling = Instelling.objects.get(site=site)
    except:
        pass
    return {
        'ENV': settings.ENV,
        'SOURCE_COMMIT': settings.SOURCE_COMMIT,
        'REGELING_COUNT': Regeling.objects.all().count(),
        'PROFIEL_COUNT': Profiel.is_zichtbaar.all().count(),
        'THEMA_COUNT': Thema.objects.all().count(),
        'SITE_INSTELLINGEN': instelling,
    }
