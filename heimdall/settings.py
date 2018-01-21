# coding: utf-8

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMMIT_DATABASE = True

DATABASES = {
    "master": {
        "type": "mongodb",
        "database": "master",
        "host": "mongodb+srv://heimdall-alwtu.mongodb.net/",
        "port": 27017,
        "username": "",
        "password": ""
    }
}

