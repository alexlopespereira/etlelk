import requests
from elketlbase import ElkEtlBase


class ElkEtlApiServicos(ElkEtlBase):

    def __init__(self, job_description, limit=1000):
        super().__init__(job_description, limit=limit)
        self.index = job_description['index-pattern']


    def load_results(self):
        if self.loaded:
            return None
        url = 'https://www.servicos.gov.br/api/v1/servicos/'
        response = requests.get(url)
        response = response.json()['resposta']
        for s in response:
            servico_id = s['id'].split('/')[6]
            cod_siorg = s['orgao']['id'].split('/')[5]
            s['cod_siorg'] = cod_siorg
            s['servico_id'] = servico_id
            s['id'] = servico_id

        self.loaded = True
        return response
