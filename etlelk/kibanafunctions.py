import json
from datetime import datetime
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
from pathlib import Path

from etlelk.elasticsearchfunctions import ElasticsearchFunctions


class KibanaFunctions:

    def __init__(self, config):
        self.config = config
        self.els = ElasticsearchFunctions(config)
        self.session = requests.Session()

    def upload_from_file(self, file, kibana_url, namespace, src_index_pattern_id=None, dest_index_pattern_id=None):
        """
        Faz upload de arquivo ndjson de objetos para o kibana
        # :param path: caminho que contem o arquivo a ser enviado
        :param file: nome do arquivo de objetos a ser enviado
        :param kibana_url: URL do kibana para upload do arquivo de objetos.
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

        multipart_data = MultipartEncoder(fields={'file': (file.name, open(file, 'rb'), 'text/plain')})
        headers = {
            'Accept': '*/*',
            'kbn-xsrf': 'true',
            'Content-Type': multipart_data.content_type}
        params = (('overwrite', 'true'),)
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)

        if namespace:
            created_space = self.els.create_space(kibana_url, namespace)
            if not created_space:
                print(f"Failed to create namespace '{namespace}'")

        import_url = f"{kibana_url}{f'/s/{namespace}' if namespace else ''}/api/saved_objects/_import"

        response = self.session.post(import_url, headers=headers, params=params, data=multipart_data, verify=False)
        if 'error' in response.text:
            raise ImportError
        return True

    def download_objects(self, job):
        """
        Copia objetos de um kibana para outro. Ex.: do desenvolvimento para produção.
        :param job:
        :return:
        """
        filename = f"objects_{job['prefix']}{datetime.today().date()}.ndjson"
        if 'namespace' in job:
            self.els.create_space(self.config.KIBANA_DEST_URL, job['namespace'])
        namespace = job['namespace'] if 'namespace' in job else None
        objs = self.get_objects_from_search(self.config.KIBANA_URL, namespace, job['prefix'])
        file = f"{self.config.DEST_PATH}/{filename}"
        with open(file, "w") as text_file:
            for o in objs:
                jsonstr = f"{json.dumps(o)}\n"
                text_file.write(jsonstr)

        # return self.uplaod_from_file(file, self.config.KIBANA_DEST_URL, namespace)

    @staticmethod
    def find_index_pattern_id(data):
        for d in data:
            if d['references'] and d['references'][0]['type'] == 'index-pattern':
                return d['references'][0]['id']
            elif d["type"] == "index-pattern":
                return d['id']
        return None

    def download_all(self):
        """
        salva no sistema de arquivos e opcionalnte copia do dev para a producao
        :return:
        """
        for j in self.config.DASHBOARDS.values():
            self.download_objects(j)

    def upload_files_replacing_index_id(self, prefix=None):
        """
        Lê do sistema de arquivos e faz um upload no kibana de desenvolvimento
        :return:
        """
        path = self.config.KIBANA_SAVED_OBJECTS_PATH
        for j in self.config.DASHBOARDS.values():
            if prefix and j['prefix'] != prefix:
                continue
            namespace = j['namespace'] if 'namespace' in j else None
            dest_index_pattern_id = self.els.get_object_id(self.config.KIBANA_DEST_URL, namespace, "index-pattern",
                                                           j['index'])
            if not dest_index_pattern_id:
                continue
            filenames = [p for p in Path(path).rglob(f"*{j['prefix']}*.ndjson")]
            if not filenames:
                continue
            filename = filenames[0]
            with open(filename, "r") as fp:
                data = fp.read()
                # jsonstr = f"[{data.replace('}' + chr(10), '},')[:-1]}]"
                jsonstr = "[{0}]".format(data.replace('}\n', '},')[:-1])
                jsondata = json.loads(jsonstr)
                src_index_pattern_id = self.find_index_pattern_id(jsondata)
                self.upload_from_file(filename, self.config.KIBANA_DEST_URL, namespace,
                                      src_index_pattern_id=src_index_pattern_id,
                                      dest_index_pattern_id=dest_index_pattern_id)

    def upload_files(self):
        """
        Lê do sistema de arquivos e faz um upload no kibana de desenvolvimento
        :return:
        """
        path = self.config.KIBANA_SAVED_OBJECTS_PATH
        for j in self.config.DASHBOARDS.values():
            filenames = [p for p in Path(path).rglob(f"*{j['prefix']}*.ndjson")]
            if not filenames:
                continue
            namespace = j['namespace'] if 'namespace' in j else None
            result = self.upload_from_file(filenames[0], self.config.KIBANA_URL, namespace)
            if result:
                print(f"uploaded {filenames[0]}")

    def is_dashboard_available(self, kibana_url, namespace, prefix):
        """
        Retorna se existe algum dashboard de um determinado namespace especificado pelo prefixo
        :param kibana_url:
        :param namespace:
        :param prefix:
        :return:
        """

        url = f"{kibana_url}{f'/s/{namespace}' if namespace else ''}/api/saved_objects/_find"

        params = (
            ('search', f'{prefix}__*'),
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
            return response.json()['total'] != 0
        else:
            return False

    def get_objects_from_search(self, kibana_url, namespace, prefix):

        url = f"{kibana_url}{f'/s/{namespace}' if namespace else ''}/api/saved_objects/_find"

        params = (
            ('search', f'{prefix}__*'),
            ('per_page', '50'),
            ('page', '1'),
            ('type', ['config', 'visualization', 'search', 'dashboard', 'index-pattern']),
            ('sort_field', 'type'),
        )
        headers = {'Content-Type': 'application/json'}
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        response = self.session.get(url, headers=headers, params=params)
        if not response.ok:
            raise ValueError
        response = response.json()
        return response['saved_objects']
