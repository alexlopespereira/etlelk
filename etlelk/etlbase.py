import json
from abc import abstractmethod
from elasticsearch.helpers import bulk

from etlelk.kibanafunctions import KibanaFunctions


class EtlBase:
    """
    Como usar esta classe:
    1) Implementar o metodo create_query. Este metodo deve levar em conta os parametros self.limit e self.offset para fazer cargas parciais, carregando uma janela de dados.
    2) Implementar o metodo load_results que deve extrair de alguma fonte os dados a serem carregados.
    Este metodo deve levar em conta os parametros self.limit e self.offset para fazer cargas parciais, carregando uma janela de dados.
    3) Implementar o metodo parse_results que faz qualquer tratamento necessário e retorna um campo que deve ter o valor único chamado "id" dentro do dicionário de cada registro
    """

    def __init__(self, config, job_description, limit=100000):
        self.index = job_description['index']
        self.query = None
        self.connection = None
        self.from_date = None
        self.offset = 0
        self.elk_settings = job_description['settings']
        self.job_description = job_description
        self.limit = limit
        self.load_finished = False
        self.chunk_size = 500
        self.inconsistencies = set([])
        self.config = config
        self.kf = KibanaFunctions(config)

    @abstractmethod
    def connect(self):
        pass

    def gendata(self):
        ans = self.load_results()
        if not ans:
            self.offset = -1
            return
        else:
            self.offset += self.limit

        if 'id' in ans[0]:
            for a in ans:
                if 'routing' in a:
                    routing = a.pop('routing')
                    doc = {"doc": a, "_id": a["id"], '_op_type': 'update', 'doc_as_upsert': True, '_index': self.index,
                           '_routing': routing}
                else:
                    doc = {"doc": a, "_id": a["id"], '_op_type': 'update', 'doc_as_upsert': True, '_index': self.index}
                yield doc
        else:
            for doc in ans:
                doc['_index'] = self.index
                yield doc

    def get_last_record(self, es):
        if 'date_field' not in self.job_description or self.job_description['date_field'] is None:
            return None
        last_record_query = {
            "sort": [
                {self.job_description['date_field']: {"order": "desc"}},
                "_score"
            ],
            "from": 0, "size": 1
        }
        resav = es.search(index=self.index, body=last_record_query)
        result = {}
        if resav['hits']['hits']:
            result[self.job_description['date_field']] = resav['hits']['hits'][0]['_source'][self.job_description['date_field']]

        return result

    def get_from_date(self, es, date_field=None):
        last_record = self.get_last_record(es)
        if last_record:
            if not date_field:
                self.from_date = last_record[self.job_description['date_field']]
            else:
                self.from_date = last_record[date_field]
        else:
            self.from_date = None

        return self.from_date

    def check_or_create_index(self, es, index=None):
        if index:
            existed_index = self.kf.els.check_or_create_index(es, index, json.dumps(self.elk_settings))
        else:
            existed_index = self.kf.els.check_or_create_index(es, self.index, json.dumps(self.elk_settings))
        return existed_index

    def create_index_pattern(self, existed_index, kibana_url, job_description=None):
        if existed_index == "CREATED":

            job_description = job_description if job_description else self.job_description

            created_space = self.kf.els.create_space(kibana_url, job_description['namespace'])
            if not created_space:
                print(f"Failed to create namespace '{job_description['namespace']}'")

            self.kf.els.create_index_pattern(kibana_url, job_description['index'], job_description['namespace'],
                                             job_description['date_field'])
            return True
        else:
            return False

    @abstractmethod
    def parse_result(self, results):
        pass

    @abstractmethod
    def load_results(self):
        pass

    @abstractmethod
    def update_by_query(self):
        """
        For post processing purposes.
        :return:
        """
        pass

    @abstractmethod
    def create_query(self, from_date=None, date_field=None):
        pass

    def report(self):
        print(self.inconsistencies)

    def run(self, es, es_url):
        self.connect()
        existed_index = self.check_or_create_index(es)
        if not existed_index:
            return False
        from_date = self.get_from_date(es)
        self.create_query(from_date)
        self.offset = 0
        while self.offset >= 0:
            bulk(es, self.gendata(), chunk_size=self.chunk_size)
        self.update_by_query()
        self.report()

    def run_once(self, es, es_url, offset=0):
        self.connect()
        existed_index = self.check_or_create_index(es)
        if not existed_index:
            return False
        from_date = self.get_from_date(es)
        self.offset = offset
        self.create_query(from_date)
        return self.load_results()
