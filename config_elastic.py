# -*- coding: utf-8 -*-
import os

from elasticsearch import Elasticsearch
from settings.settings_generic import body_settings_generic


DEST_PATH = os.environ.get('DEST_PATH') or "."
ES_HOST = os.environ.get('ES_HOST') or 'localhost'
ES_PORT = os.environ.get('ES_PORT') or '9200'
ES_USER = os.environ.get('ES_USER') or 'admin'
ES_PASSWORD = os.environ.get('ES_PASSWORD') or 'pass'
ES_USE_SSL = os.environ.get('ES_USE_SSL') == "True"
ES_SERVICOS_INDEX = os.environ.get('ES_SERVICOS_INDEX') or 'servicos'
ES_INDEX2 = os.environ.get('ES_INDEX2') or 'index2'

job_servicos = {"index-pattern": ES_SERVICOS_INDEX, "settings": body_settings_generic, "prefix": "SERVICOS__", "namespace": "servicos", "date_field": "date", "description": "Servicos", "module_name": "elk.ElkEtlApiServicos", "class_name": "ElkEtlApiServicos", "kibana_date_format": "yyyy-MM-dd HH:mm:ss"}
# job2 = {"control_id": "1574951280225", "index-pattern": ES_INDEX2, "settings": body_settings_generic, "prefix": "INDEX2__", "namespace": "test", "date_field": "date", "description": "Index 2", "module_name": "elk.ElkEtlApiServicos", "class_name": "ElkEtlApiServicos", "kibana_date_format": "yyyy-MM-dd"}


INDEXES = [job_servicos]


es = Elasticsearch(
    hosts=[{'host': ES_HOST, 'port': ES_PORT}],
    http_auth=(ES_USER, ES_PASSWORD),
    use_ssl=ES_USE_SSL,
    verify_certs=False
)


