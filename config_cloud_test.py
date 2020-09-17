import os
from elasticsearch import Elasticsearch

from etlelk.configbase import ConfigBase
from etlelk.settings_generic import body_settings_generic


class Config(ConfigBase):
    KIBANA_SAVED_OBJECTS_PATH = os.environ.get('KIBANA_SAVED_OBJECTS_PATH', ".")
    KIBANA_HOST = os.environ.get('ES_HOST', 'localhost')
    KIBANA_PORT = os.environ.get('ES_PORT', '5601')
    ES_HOST = os.environ.get('ES_HOST', 'localhost')
    ES_PORT = os.environ.get('ES_PORT', '9200')
    ES_USER = os.environ.get('ES_USER', 'admin')
    ES_PASSWORD = os.environ.get('ES_PASSWORD', 'pass')
    ES_USE_SSL = os.environ.get('ES_USE_SSL') == "True"
    ES_SERVICOS_INDEX = os.environ.get('ES_SERVICOS_INDEX', 'servicos')
    ES_SOURCECODE_INDEX = os.environ.get('ES_SOURCECODE_INDEX', 'sourcecode')
    ES_TAGCLOUD_INDEX = os.environ.get('ES_TAGCLOUD_INDEX', 'tagcloud')

    es_kb_protocol = 'https' if ES_USE_SSL else 'http'

    ES_URL = f"{es_kb_protocol}://{ES_HOST}:{ES_PORT}"
    KIBANA_URL = f"{es_kb_protocol}://{KIBANA_HOST}:{KIBANA_PORT}"

    es = Elasticsearch(
        cloud_id=ES_CLOUD_ID,
        http_auth=(ES_USER, ES_PASSWORD),
    )

    job_tagcloud = {"index": ES_TAGCLOUD_INDEX, "settings": body_settings_generic, "prefix": "TAGCLOUD__",
                    "description": "Tag Cloud", "module_name": "ElkEtlTagCloud",
                    "class_name": "ElkEtlTagCloud", "es": es}
    
    INDEXES = {'tagcloud': job_tagcloud}
