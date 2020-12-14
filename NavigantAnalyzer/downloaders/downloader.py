import requests
import json
from .rastilippu import rastilippu_download
from .navisport import navisport_download

NAVIGANT_API_URL = 'https://api.navigant.fi/results?event={}&raw=true'

def download_from_url(url):
    splitted_url = url.split("/")
    server_address = splitted_url[2]
    if server_address.endswith('navisport.fi'):
        return navisport_download(url)
    elif server_address.endswith('rastilippu.fi'):
        return rastilippu_download(url)
    else:
        #This is the old default format
        navigant_id = splitted_url[-1]
        api_url = NAVIGANT_API_URL.format(navigant_id)
        try:
            response = requests.get(api_url)
            if len(response.text) > 10:
                # The event was found in Navigant API
                return json.loads(response.text)
            else:
                return dict()
        except:
            return dict()

def download_from_file(f):
    try:
        return json.load(f)
    except:
        return dict()

def download_from_ext_input(url, raw_data_file):
    if url:
        ext_input = download_from_url(url)
    else:
        ext_input = download_from_file(raw_data_file)
    return ext_input
