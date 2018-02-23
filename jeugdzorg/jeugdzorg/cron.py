from jeugdzorg.models import Regeling
import requests
from bs4 import BeautifulSoup
import json
import datetime


def update_regeling_bron_job():
    for regeling in Regeling.objects.all():
        if regeling.bron_url and regeling.bron_html_query:
            result = requests.request('get', regeling.bron_url)
            soup = BeautifulSoup(result.text, "html.parser")
            soup_result = []
            for link in soup.select(regeling.bron_html_query):
                soup_result.append(link.text)
                print(hash(json.dumps(soup_result)))
            h = json.dumps(soup_result)
            if h != regeling.bron_resultaat and not regeling.bron_veranderd:
                regeling.bron_veranderd = True
                regeling.bron_resultaat = h
                regeling.save()

