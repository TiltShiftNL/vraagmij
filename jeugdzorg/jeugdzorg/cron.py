from jeugdzorg.models import Regeling
import requests
from bs4 import BeautifulSoup
import json

def update_regeling_bron_job():
    for regeling in Regeling.objects.all():
        if regeling.bron_url and regeling.bron_html_query:
            result = requests.request('get', regeling.bron_url)
            soup = BeautifulSoup(result.text, "html.parser")
            # print(result.text)
            soup_result = []
            # json_result = json.dumps(soup.select(regeling.bron_html_query))
            for link in soup.select(regeling.bron_html_query):
                # print(json_result)
                # print(link.text)
                soup_result.append(link.text)
            print(hash(json.dumps(soup_result)))
            regeling.bron_result = hash(json.dumps(soup_result))
            regeling.save()

