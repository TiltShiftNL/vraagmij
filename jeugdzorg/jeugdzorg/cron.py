from jeugdzorg.models import Regeling
import requests
from bs4 import BeautifulSoup
import json
import datetime
import hashlib


def print_variables():
    from django.conf import settings
    print('settings.ENV')
    print(settings.ENV)
    print('settings.POSTGRES_HOST')
    print(settings.POSTGRES_HOST)
    print('---')


def update_regeling_bron_job():
    print('START JOB update_regelingen')
    for regeling in Regeling.objects.all():
        if regeling.bron_url:
            query = regeling.bron_html_query
            if not query:
                query = 'body'
            result = requests.request('get', regeling.bron_url)
            soup = BeautifulSoup(result.text, "html.parser")
            soup_result = []
            for link in soup.select(query):
                soup_result.append(link.text)
            h = json.dumps(soup_result)
            #h = hashlib.sha1(json.dumps(soup_result).encode('utf-8')).hexdigest()
            print('regeling id:%s' % regeling.id)
            print(h)
            if h != regeling.bron_resultaat and not regeling.bron_veranderd:
                regeling.bron_resultaat = h
                regeling.bron_veranderd = True
                regeling.save()
        else:
            regeling.bron_veranderd = False
            regeling.save()


