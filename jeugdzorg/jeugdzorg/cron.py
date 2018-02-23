from jeugdzorg.models import Regeling
import requests
from bs4 import BeautifulSoup
import json
import datetime
import hashlib


def update_regeling_bron_job():
    for regeling in Regeling.objects.all():
        if regeling.bron_url and regeling.bron_html_query:
            result = requests.request('get', regeling.bron_url)
            soup = BeautifulSoup(result.text, "html.parser")
            soup_result = []
            for link in soup.select(regeling.bron_html_query):
                soup_result.append(link.text)
            h = json.dumps(soup_result)
            #h = hashlib.sha1(json.dumps(soup_result).encode('utf-8')).hexdigest()
            print(h)
            if h != regeling.bron_resultaat and not regeling.bron_veranderd:
                regeling.bron_resultaat = h
                regeling.bron_veranderd = True
                regeling.save()
        else:
            regeling.bron_veranderd = False
            regeling.save()


