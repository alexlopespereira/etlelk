from importlib import import_module
### Não retirar o import abaixo. O ETL não é executado sem este import
from config_elastic import es, INDEXES, DEST_KIBANA_URL, ES_URL


def run_etl_job(job_description):
    module = import_module(job_description['module_name'])
    Cls = getattr(module, job_description['class_name'])
    o = Cls(job_description)
    o.run(es, ES_URL, DEST_KIBANA_URL)


def run_all_etls(indexes):
    for i in indexes:
        print(i)
        run_etl_job(i)


