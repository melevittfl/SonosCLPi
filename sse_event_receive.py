from config import *
import json
import pprint
import sseclient
import requests


def with_requests(url):
    proxies = {
        'http': 'http://127.0.0.1:9999',
        'https': 'http://127.0.0.1:9999',
    }

    headers = {
        'x-api-key': CL_API_KEY,
    }

    return requests.get(url, stream=True, headers=headers, proxies=proxies, verify=False)


url = 'https://demo.competitionlabs.com/api/marktest1/sse/events'

response = with_requests(url)

client = sseclient.SSEClient(response)

for event in client.events():
    pprint.pprint(json.loads(event.data))

