import os
from elasticsearch import Elasticsearch
from etlelk.settings_generic import body_settings_generic


class ConfigBase:
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
        hosts=[{'host': ES_HOST, 'port': ES_PORT}],
        http_auth=(ES_USER, ES_PASSWORD),
        use_ssl=ES_USE_SSL,
        verify_certs=False
    )

    # job_sourcecode = {"index": ES_SOURCECODE_INDEX, "settings": body_settings_sourcecode, "prefix": "SOURCECODE__",
    #                  "date_field": "date_modified", "description": "Source Code", "module_name": "ElkEtlPythonCode",
    #                  "class_name": "ElkEtlPythonCode", "src_path": "../data"}
    
    job_tagcloud = {"index": ES_TAGCLOUD_INDEX, "settings": body_settings_generic,
                    "namespace": "default",
                    "module_name": "ElkEtlTagCloud", "class_name": "ElkEtlTagCloud", "es": es}

    INDEXES = {"job_tagcloud": job_tagcloud}
    DASH_TAGCLOUD = {"index": ES_TAGCLOUD_INDEX, "prefix": ES_TAGCLOUD_INDEX.split("__")[0], "namespace": "default"}
    DASHBOARDS = {'tagcloud': DASH_TAGCLOUD}
