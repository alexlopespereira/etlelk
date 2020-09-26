from time import sleep

import requests
from elasticsearch_dsl import UpdateByQuery


class ElasticsearchFunctions:

    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

    @staticmethod
    def check_or_create_index(esc, index_name, settings):
        response = esc.indices.exists(index_name)
        if response is True:
            return "EXISTED"
        else:
            esc.indices.create(index_name, body=settings)
            return "CREATED"

    def create_index_pattern(self, dest_es_url, index_patter_name, namespace, date_field):
        headers = {'Accept': '*/*', 'kbn-xsrf': 'true', 'Content-Type': 'application/json'}
        data = f'{{"attributes":{{"title":"{index_patter_name}","timeFieldName":"{date_field}"}}}}'
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)

        post_url = f"{dest_es_url}{f'/s/{namespace}' if namespace else ''}/api/saved_objects/index-pattern"

        response = self.session.post(post_url, headers=headers, data=data)

        if response.status_code == 200:
            return True
        else:
            print(f"error creating index {index_patter_name} on {dest_es_url}")
            return False

    def create_space(self, url, namespace):
        headers = {'kbn-xsrf': 'true', 'Content-Type': 'application/json'}
        data = f'{{"id": "{namespace}", "name": "{namespace}", "initials": "{namespace.upper()[0:2]}", ' \
               f'"disabledFeatures":[]}}'
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        response = self.session.post(f'{url}/api/spaces/space', headers=headers, data=data)
        return response == 200

    def get_object_id(self, kib_url, namespace, type_str, name):

        url = f"{kib_url}{f'/s/{namespace}' if namespace else ''}/api/saved_objects/_find"

        params = (
            ('type', type_str),
            ('search_fields', 'title'),
            ('search', name),
        )
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        response = self.session.get(url, params=params, verify=False)
        if response.status_code != 200:
            print(f"{response.status_code}, {self.config.ES_USER}, {self.config.ES_PASSWORD}, {url}")
            return None

        response_json = response.json()
        if 'total' in response_json and response_json['total'] > 0:
            return response_json['saved_objects'][0]['id']
        else:
            return None

    def get_index_pattern(self, url, namespace, id_str):
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }
        data = f'[{{"id":"{str(id_str)}","type":"index-pattern"}}]'
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)

        bulk_url = f"{url}{f'/s/{namespace}' if namespace else ''}/api/saved_objects/_bulk_get"

        response = self.session.post(bulk_url, headers=headers, data=data)
        return response.json()

    @staticmethod
    def check_index_not_empty(index, esc):
        empty_query = {}
        resav = esc.search(index=index, body=empty_query)
        return len(resav['hits']['hits']) > 0

    @staticmethod
    def delete_from_day(esc, index, from_date, to_date):

        query = '''{
                      "query": {
                            "range" : {
                                "updated" : {
                                    "gte" : "%s",
                                    "lte" : "%s"
                                }
                            }
                        }
                    }''' % (from_date, to_date)
        result = esc.delete_by_query(index, query)
        return result

    @staticmethod
    def delete_index(esc, index):
        esc.indices.delete(index=index, ignore=[400, 404])

    @staticmethod
    def run_update_by_query(esc, query, index):

        ubq = UpdateByQuery(using=esc, index=index).update_from_dict(
            query).params(request_timeout=100)
        finished = False
        count = 0
        while not finished and count < 3:
            try:
                count += 1
                response = ubq.execute()
                finished = True
            except Exception as e:
                print(e)
                sleep(10 * count)
                pass