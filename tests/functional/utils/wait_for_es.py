import sys
import time

from elasticsearch import Elasticsearch

sys.path.append('/usr/src/tests/')
from settings import test_settings

es = Elasticsearch(
    [f'{test_settings.es_host}:'
     f'{test_settings.es_port}'],
    verify_certs=True)

while not es.ping():
    print('Elasticsearch not connected. Wait 10 seconds...')
    time.sleep(10)
else:
    print('Elasticsearch connected.')
