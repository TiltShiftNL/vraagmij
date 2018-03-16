# -*- coding: utf-8 -*-
from django.conf import settings
from jeugdzorg.models import Regeling
from jeugdzorg.models import Profiel
from jeugdzorg.models import Thema


def app_settings(request):

    return {
        'ENV': settings.ENV,
        'SOURCE_COMMIT': settings.SOURCE_COMMIT,
        'UWSGI_TEST': request.environ.get('UWSGI_TEST'),
        'REGELING_COUNT': Regeling.objects.all().count(),
        'PROFIEL_COUNT': Profiel.is_zichtbaar.all().count(),
        'THEMA_COUNT': Thema.objects.all().count()
    }
