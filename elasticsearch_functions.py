import requests
from config_elastic import config #ES_USER, ES_PASSWORD, es

session = requests.Session()


def check_or_create_index(es_url, index_name, settings):
    url = es_url + "/" + index_name
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    response = session.get(url, verify=False)
    if response.status_code == 401:
        print("Not authorize user: {0}, pass: {1}".format(config['ES_USER'], config['ES_PASSWORD']))
        return None
    response = response.json()

    if 'error' in response:
        headers = {'Content-Type': 'application/json'}
        response = session.put(url, headers=headers, data=settings)

        if response.status_code == 200:
            data = '{"index.max_result_window" : "20000"}'
            response = session.put(es_url + '/_settings', headers=headers, data=data)
        else:
            return None

        return "CREATED"
    else:
        return "EXISTED"


def create_index_pattern(dest_es_url, index_patter_name, namespace, date_field):
    headers = {'Accept': '*/*', 'kbn-xsrf': 'true', 'Content-Type': 'application/json'}
    data = '{"attributes":{"title":"' + index_patter_name + '","timeFieldName":"' + date_field + '"}}'
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    response = session.post(dest_es_url + "/s/" + namespace + "/api/saved_objects/index-pattern", headers=headers, data=data)
    if response.status_code != 200:
        print("error creating index {0} on {1}".format(index_patter_name, dest_es_url))
        return


def create_space(url, namespace):
    headers = {'kbn-xsrf': 'true', 'Content-Type': 'application/json'}
    data = '{"id": "' + namespace + '", "name": "' + namespace + '", "initials": "' + namespace.upper()[0:2] + '", "disabledFeatures":[]}'
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    response = session.post(url + '/api/spaces/space', headers=headers, data=data)
    return response == 200


def get_object_id(kib_url, namespace, type, name):
    url = kib_url + "/s/" + namespace + "/api/saved_objects/_find"
    params = (
        ('type', type),
        ('search_fields', 'title'),
        ('search', name),
    )
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    response = session.get(url, params=params)
    if response.status_code != 200:
        print("{0}, {1}, {2}, {3}".format(response.status_code, config['ES_USER'], config['ES_PASSWORD'], url))
        return None

    response_json = response.json()
    if 'total' in response_json and response_json['total'] > 0:
        return response_json['saved_objects'][0]['id']
    else:
        return None


def get_objects_from_search(es_url, namespace, prefix):
    url = es_url + "/s/" + namespace + "/api/saved_objects/_find"
    params = (
        ('search', '{0}*'.format(prefix)),
        ('per_page', '50'),
        ('page', '1'),
        ('type', ['config', 'visualization', 'search', 'dashboard', 'index-pattern']),
        ('sort_field', 'type'),
    )
    headers = {'Content-Type': 'application/json'}
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    response = session.get(url, headers=headers, params=params)
    response = response.json()
    return response['saved_objects']


def get_index_pattern(url, namespace, id):
    headers = {
        'Accept': '*/*',
        'Content-Type': 'application/json'
    }
    data = '[{"id":"' + str(id) + '","type":"index-pattern"}]'
    session.auth = (config['ES_USER'], config['ES_PASSWORD'])
    response = session.post('{0}/s/{1}/api/saved_objects/_bulk_get'.format(url, namespace), headers=headers, data=data)
    return response.json()


def check_index_not_empty(index, esc):
    empty_query = {}
    resav = esc.search(index=index, body=empty_query)
    return len(resav['hits']['hits']) > 0


def delete_from_day(esc, index, from_day):

    query = '''{
                  "query": {
                        "range" : {
                            "updated" : {
                                "gte" : "%s"
                            }
                        }
                    }
                }''' % (from_day)
    result = esc.delete_by_query(index, query)
    return result
