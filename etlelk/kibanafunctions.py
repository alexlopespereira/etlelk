import json
from datetime import datetime
import requests
# from config_elastic import config
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pathlib import Path

from etlelk.elasticsearchfunctions import ElasticsearchFunctions # import create_index_pattern, create_space, get_object_id, get_objects_from_search



class KibanaFunctions:

    def __init__(self, config):
        self.config = config
        self.els = ElasticsearchFunctions(config)
        self.session = requests.Session()


    def uplaod_from_file(self, file, url, namespace, src_index_pattern_id=None, dest_index_pattern_id=None):
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
        # file = path + "/" + filename

        if src_index_pattern_id and dest_index_pattern_id:
            with open(file, "r") as fp:
                data = fp.read()
            data = data.replace(src_index_pattern_id, dest_index_pattern_id)
            with open(file, "w") as fp:
                fp.write(data)

        multipart_data = MultipartEncoder(fields={'file': (file, open(file, 'rb'), 'text/plain')})
        headers = {
            'Accept': '*/*',
            'kbn-xsrf': 'true',
            'Content-Type': multipart_data.content_type}
        params = (('overwrite', 'true'),)
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        if namespace:
            created_space = self.els.create_space(url, namespace)
            print(created_space)
            import_url = url + "/s/" + namespace + '/api/saved_objects/_import'
        else:
            import_url = url + '/api/saved_objects/_import'

        response = self.session.post(import_url, headers=headers, params=params, data=multipart_data)
        if 'error' in response.text:
            raise ImportError
        return True

    def download_objects(self, job):
        """
        Copia objetos de um kibana para outro. Ex.: do desenvolvimento para produção.
        :param job:
        :return:
        """
        filename = "objects_{0}{1}.ndjson".format(job['prefix'], datetime.today().date())
        if 'namespace' in job:
            self.els.create_space(self.config.KIBANA_DEST_URL, job['namespace'])
        namespace = job['namespace'] if 'namespace' in job else None
        objs = self.els.get_objects_from_search(self.config.KIBANA_URL, namespace, job['prefix'])
        file = self.config.DEST_PATH + "/" + filename
        with open(file, "w") as text_file:
            for o in objs:
                jsonstr = json.dumps(o) + "\n"
                text_file.write(jsonstr)

        # return self.uplaod_from_file(file, self.config.KIBANA_DEST_URL, namespace)

    def find_index_pattern_id(self, data):
        for d in data:
            if d['references'] and d['references'][0]['type'] == 'index-pattern':
                return d['references'][0]['id']
            elif d["type"]=="index-pattern":
                return d['id']
        return None

    def download_all(self):
        """
        salva no sistema de arquivos e opcionalnte copia do dev para a producao
        :return:
        """
        for j in self.config.INDEXES:
            self.download_objects(j)

    def upload_files_replacing_index_id(self):
        """
        Lê do sistema de arquivos e faz um upload no kibana de desenvolvimento
        :return:
        """
        path = "../saved_objects"
        for j in self.config.INDEXES:
            namespace = j['namespace'] if 'namespace' in j else None
            dest_index_pattern_id = self.els.get_object_id(self.config.KIBANA_DEST_URL, namespace, "index-pattern", j['index'])
            if not dest_index_pattern_id:
                continue
            filename = "objects_{0}{1}.ndjson".format(j['prefix'], datetime.today().strftime("%Y-%m-%d"))
            with open(path + "/" + filename, "r") as fp:
                data = fp.read()
                jsonstr = "[{0}]".format(data.replace('}\n', '},')[:-1])
                jsondata = json.loads(jsonstr)
                src_index_pattern_id = self.find_index_pattern_id(jsondata)
                self.uplaod_from_file(path + "/" + filename, self.config.KIBANA_DEST_URL, namespace,
                                          src_index_pattern_id=src_index_pattern_id, dest_index_pattern_id=dest_index_pattern_id)


    def upload_files(self):
        """
        Lê do sistema de arquivos e faz um upload no kibana de desenvolvimento
        :return:
        """
        path = "../saved_objects"
        for j in self.config.INDEXES:
            filenames = [p for p in Path(path).rglob('*{0}*.ndjson'.format(j['prefix']))]
            namespace = j['namespace'] if 'namespace' in j else None
            self.uplaod_from_file(filenames[0], self.config.KIBANA_URL, namespace)

    def is_dashboard_available(self, es_url, namespace, prefix):
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
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        try:
            response = self.session.get(url, headers=headers, params=params)
        except Exception as e:
            print(e)
            pass
            return None
        if response.ok:
            return response.json()['total'] is not 0
        else:
            return False
