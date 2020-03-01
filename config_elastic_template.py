# -*- coding: utf-8 -*-
import os
from collections import defaultdict

from elasticsearch import Elasticsearch
from settings_generic import body_settings_generic

config = defaultdict()
config['DEST_PATH'] = os.environ.get('DEST_PATH') or "."
config['ES_HOST'] = os.environ.get('ES_HOST') or 'localhost'
config['ES_PORT'] = os.environ.get('ES_PORT') or '9200'
config['ES_USER'] = os.environ.get('ES_USER') or 'admin'
config['ES_PASSWORD'] = os.environ.get('ES_PASSWORD') or 'pass'
config['ES_USE_SSL'] = os.environ.get('ES_USE_SSL') == "True"
config['ES_SERVICOS_INDEX'] = os.environ.get('ES_SERVICOS_INDEX') or 'servicos'
config['ES_INDEX2'] = os.environ.get('ES_INDEX2') or 'index2'
config['DEST_KIBANA_URL'] = os.environ.get('DEST_KIBANA_URL') or 'localhost:5601'

ES_INDEX2 = os.environ.get('ES_INDEX2') or 'index2'

if config['ES_USE_SSL']:
    config['ES_URL'] = "https://{0}:{1}".format(config['ES_HOST'], config['ES_PORT'])
else:
    config['ES_URL'] = "http://{0}:{1}".format(config['ES_HOST'], config['ES_PORT'])


job_servicos = {"index-pattern": config['ES_SERVICOS_INDEX'], "settings": body_settings_generic, "prefix": "SERVICOS__", "namespace": "servicos", "date_field": "date", "description": "Servicos", "module_name": "elk.ElkEtlApiServicos", "class_name": "ElkEtlApiServicos", "kibana_date_format": "yyyy-MM-dd HH:mm:ss"}
# job2 = {"control_id": "1574951280225", "index-pattern": ES_INDEX2, "settings": body_settings_generic, "prefix": "INDEX2__", "namespace": "test", "date_field": "date", "description": "Index 2", "module_name": "elk.ElkEtlApiServicos", "class_name": "ElkEtlApiServicos", "kibana_date_format": "yyyy-MM-dd"}


config['INDEXES'] = [job_servicos]


es = Elasticsearch(
    hosts=[{'host': config['ES_HOST'], 'port': config['ES_PORT']}],
    http_auth=(config['ES_USER'], config['ES_PASSWORD']),
    use_ssl=config['ES_USE_SSL'],
    verify_certs=False
)

config['es'] = es

