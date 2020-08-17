import requests



class ElasticsearchFunctions:

    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

    def check_or_create_index(self, esc, index_name, settings):
        response = esc.indices.exists(index_name)
        if response is True:
            return "EXISTED"
        else:
            esc.indices.create(index_name, body=settings)
            return "CREATED"

    def create_index_pattern(self, dest_es_url, index_patter_name, namespace, date_field):
        headers = {'Accept': '*/*', 'kbn-xsrf': 'true', 'Content-Type': 'application/json'}
        data = '{"attributes":{"title":"' + index_patter_name + '","timeFieldName":"' + date_field + '"}}'
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        if namespace:
            post_url = dest_es_url + "/s/" + namespace + "/api/saved_objects/index-pattern"
        else:
            post_url = dest_es_url + "/api/saved_objects/index-pattern"

        response = self.session.post(post_url, headers=headers, data=data)
        if response.status_code != 200:
            print("error creating index {0} on {1}".format(index_patter_name, dest_es_url))
            return

    def create_space(self, url, namespace):
        headers = {'kbn-xsrf': 'true', 'Content-Type': 'application/json'}
        data = '{"id": "' + namespace + '", "name": "' + namespace + '", "initials": "' + namespace.upper()[0:2] + '", "disabledFeatures":[]}'
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        response = self.session.post(url + '/api/spaces/space', headers=headers, data=data)
        return response == 200

    def get_object_id(self, kib_url, namespace, type, name):
        if namespace:
            url = kib_url + "/s/" + namespace + "/api/saved_objects/_find"
        else:
            url = kib_url + "/api/saved_objects/_find"

        params = (
            ('type', type),
            ('search_fields', 'title'),
            ('search', name),
        )
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        response = self.session.get(url, params=params, verify=False)
        if response.status_code != 200:
            print("{0}, {1}, {2}, {3}".format(response.status_code, self.config.ES_USER, self.config.ES_PASSWORD, url))
            return None

        response_json = response.json()
        if 'total' in response_json and response_json['total'] > 0:
            return response_json['saved_objects'][0]['id']
        else:
            return None

    def get_index_pattern(self, url, namespace, id):
        headers = {
            'Accept': '*/*',
            'Content-Type': 'application/json'
        }
        data = '[{"id":"' + str(id) + '","type":"index-pattern"}]'
        self.session.auth = (self.config.ES_USER, self.config.ES_PASSWORD)
        if namespace:
            bulk_url = '{0}/s/{1}/api/saved_objects/_bulk_get'.format(url, namespace)
        else:
            bulk_url = '{0}/api/saved_objects/_bulk_get'.format(url)

        response = self.session.post(bulk_url, headers=headers, data=data)
        return response.json()

    def check_index_not_empty(self, index, esc):
        empty_query = {}
        resav = esc.search(index=index, body=empty_query)
        return len(resav['hits']['hits']) > 0

    def delete_from_day(self, esc, index, from_date, to_date):

        query = '''{
                      "query": {
                            "range" : {
                                "updated" : {
                                    "gte" : "%s",
                                    "lte" : "%s"
                                }
                            }
                        }
                    }'''% (from_date, to_date)
        result = esc.delete_by_query(index, query)
        return result

    def delete_index(self, esc, index):
        esc.indices.delete(index=index, ignore=[400, 404])
