# -*- coding: utf-8 -*-
from django.conf import settings
from jeugdzorg.models import Regeling
from jeugdzorg.models import Profiel
from jeugdzorg.models import Thema
from django.contrib.sites.models import Site


def app_settings(request=None):
    return {
        'ENV': settings.ENV,
        'SOURCE_COMMIT': settings.SOURCE_COMMIT,
        'REGELING_COUNT': Regeling.objects.all().count(),
        'PROFIEL_COUNT': Profiel.is_zichtbaar.all().count(),
        'THEMA_COUNT': Thema.objects.all().count(),
        'SITE_INSTELLINGEN': Site.objects.get_current().instelling,
    }
