from etlelk import KibanaFunctions
from etlelk.run_etl_jobs import run_etl_job

from config_cloud_test import Config

config = Config()
kf = KibanaFunctions(config)
# kf.els.delete_index(config.es, config.INDEXES[3]['index'])

# kf.els.check_or_create_index(config.es, config.INDEXES['apps']['index'], config.INDEXES['apps']['settings'])