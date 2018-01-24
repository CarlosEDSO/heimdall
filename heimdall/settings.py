# coding: utf-8

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT_DATABASE = True
ENVIRONMENT_DATABASE = 'master'
DEFAULT_OUTPUT_PATH = '{base_dir}/heimdall/output/'.format(base_dir=BASE_DIR)

DATABASES = {
    "master": {
        "type": "mongodb",
        "database": "master",
        "host": "",
        "port": 27017,
        "username": "",
        "password": ""
    }
}
