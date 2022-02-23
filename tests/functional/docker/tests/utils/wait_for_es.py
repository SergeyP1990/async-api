import time

from elasticsearch import Elasticsearch

from settings import test_settings

es = Elasticsearch(
    [f'{test_settings.es_host}:'
     f'{test_settings.es_port}'],
    verify_certs=True)


def wait_for_es():
    while not es.ping():
        print('Elasticsearch not connected. Wait 10 seconds...')
        time.sleep(10)
    else:
        print('Elasticsearch connected.')
