import json
from datetime import datetime
import requests
from config_elastic import config
from requests_toolbelt.multipart.encoder import MultipartEncoder

from elasticsearch_functions import create_index_pattern, create_space, get_object_id, get_objects_from_search

session = requests.Session()


def uplaod_from_file(path, filename, url, namespace, src_index_pattern_id=None, dest_index_pattern_id=None):
    """
    Faz upload de arquivo ndjson de objetos para o kibana
    :param path: caminho que contem o arquivo a ser enviado
    :param filename: nome do arquivo de objetos a ser enviado
    :param url: URL do kibana para upload do arquivo de objetos.
    :param namespace: space de destino
    :param src_index_pattern_id: caso seja necessário, representa o index_pattern a ser substituido
    :param dest_index_pattern_id: caso seja necessário, representa o index_pattern que vai substituir o antigo
    :return:
    """
    file = path + "/" + filename
    import_url = url + "/s/" + namespace + '/api/saved_objects/_import'

    if src_index_pattern_id and dest_index_pattern_id:
        with open(file, "r") as fp:
            data = fp.read()
        data = data.replace(src_index_pattern_id, dest_index_pattern_id)
        with open(file, "w") as fp:
            fp.write(data)

    multipart_data = MultipartEncoder(fields={'file': (filename, open(file, 'rb'), 'text/plain')})
    headers = {
        'Accept': '*/*',
        'kbn-xsrf': 'true',
        'Content-Type': multipart_data.content_type}
    params = (('overwrite', 'true'),)
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    created_space = create_space(url, namespace)
    print(created_space)
    response = session.post(import_url, headers=headers, params=params, data=multipart_data)
    if 'error' in response.text:
        raise ImportError
    return True


def copy_save_objects(src_kib_url, dest_es_url, namespace, prefix, filename):
    """
    Copia objetos de um kibana para outro. Ex.: do desenvolvimento para produção.
    :param src_kib_url:
    :param dest_es_url:
    :param index_patter_name:
    :param namespace:
    :param prefix:
    :param filename:
    :param save_to_file:
    :return:
    """
    create_space(dest_es_url, namespace)
    objs = get_objects_from_search(src_kib_url, namespace, prefix)
    file = config['DEST_PATH'] + "/" + filename
    with open(file, "w") as text_file:
        for o in objs:
            jsonstr = json.dumps(o) + "\n"
            text_file.write(jsonstr)

    return uplaod_from_file(config['DEST_PATH'], filename, dest_es_url, namespace)


def find_index_pattern_id(data):
    for d in data:
        if d['references'] and d['references'][0]['type'] == 'index-pattern':
            return d['references'][0]['id']
    return None


def copy_job_objects(job, src_kibana_url, dest_kibana_url, save_only=False):
    filename = "objects_{0}{1}.ndjson".format(job['prefix'], datetime.today().date())
    copy_save_objects(src_kibana_url, dest_kibana_url, job['index-pattern'], job['namespace'], job['prefix'], filename, job['date_field'], save_only)


def copy_all(src_kibana_url, dest_kibana_url):
    """
    salva no sistema de arquivos e opcionalnte copia do dev para a producao
    :param save_only: Caso True, apenas salva os arquivos no sistema de arquivos. Não copia para produção.
    :return:
    """
    for j in config['INDEXES']:
        filename = "objects_{0}{1}.ndjson".format(j['prefix'], datetime.today().date())
        copy_save_objects(src_kibana_url, dest_kibana_url, j['namespace'], j['prefix'], filename)


def replace_id_upload_files(dest_kibana_url):
    """
    Lê do sistema de arquivos e faz um upload no kibana de desenvolvimento
    :return:
    """
    path = "./saved_objects"
    for j in config['INDEXES']:
        dest_index_pattern_id = get_object_id(dest_kibana_url, j['namespace'], "index-pattern", j['index-pattern'])
        if not dest_index_pattern_id:
            continue
        filename = "objects_{0}{1}.ndjson".format(j['prefix'], "2020-01-17")
        with open(path+"/"+filename, "r") as fp:
            data = fp.read()
            jsonstr = "[{0}]".format(data.replace('}\n', '},')[:-1])
            jsondata = json.loads(jsonstr)
            src_index_pattern_id = find_index_pattern_id(jsondata)
            uplaod_from_file(path, filename, dest_kibana_url, j['namespace'],
                         src_index_pattern_id=src_index_pattern_id, dest_index_pattern_id=dest_index_pattern_id)


def upload_files(dest_kibana_url):
    """
    Lê do sistema de arquivos e faz um upload no kibana de desenvolvimento
    :return:
    """
    path = "./saved_objects"
    for j in config['INDEXES']:
        filename = "objects_{0}{1}.ndjson".format(j['prefix'], "2020-01-17")
        uplaod_from_file(path, filename, dest_kibana_url, j['namespace'])


def is_dashboard_available(es_url, namespace, prefix):
    """
    Retorna se existe algum dashboard de um determinado namespace especificado pelo prefixo
    :param es_url:
    :param namespace:
    :param prefix:
    :return:
    """
    url = es_url + "/s/" + namespace + "/api/saved_objects/_find"
    params = (
        ('search', '{0}*'.format(prefix)),
        ('per_page', '1'),
        ('page', '1'),
        ('type', ['dashboard']),
        # ('sort_field', 'type'),
    )
    headers = {'Content-Type': 'application/json'}
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    try:
        response = session.get(url, headers=headers, params=params)
    except Exception as e:
        print(e)
        pass
        return None
    if response.ok:
        return response.json()['total'] is not 0
    else:
        return False

