from importlib import import_module


def run_etl_job(config, job_description):
    module = import_module(job_description['module_name'])
    Cls = getattr(module, job_description['class_name'])
    o = Cls(config, job_description)
    o.run(config.es, config.ES_URL)


def run_all_etls(config):
    for i in config.INDEXES:
        print(i)
        run_etl_job(config, i)


