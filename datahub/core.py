# -*- coding: utf-8 -*-

'''
    File name: core.py
    Python Version: 3.6.1
'''

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

import os
from datetime import datetime

import pymongo.errors
from pymongo import MongoClient

from heimdall.settings import DATABASES, COMMIT_DATABASE
from heimdall.utils import adjust_lower_strip_underscore


def get_connection(info):
    if adjust_lower_strip_underscore(info['type']) == 'mongodb':
        try:
            return MongoClient(info['host'], username=info['username'],
                               password=info['password'], ssl=True, authSource='admin')
        except pymongo.errors.ConfigurationError as e:
            print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] data_hub.get_connection >> Verify host and port @ {e}'.format(
                dt=datetime.now(),
                pid=os.getpid(),
                e=e
            ))
        except Exception as e:
            print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] data_hub.get_connection >> Error @ {e}'.format(
                dt=datetime.now(),
                pid=os.getpid(),
                e=e
            ))

    return None


def insert_data(idataset, data_type, name_database, verbose=False):
    '''
    
    :param idataset: list
    :param data_type: str
    :param name_database: str 
    :param verbose: bool
    :return: 
    '''

    if name_database in DATABASES.keys() and COMMIT_DATABASE:
        infodb = DATABASES[name_database]
        if adjust_lower_strip_underscore(infodb['type']) == 'mongodb':
            client = get_connection(info=infodb)
            if client:
                banco = client[infodb['database']]
                if adjust_lower_strip_underscore(data_type) == 'weather_station_data':
                    medicao = banco['weather_data']
                # Pode vir a abranger outros tipos de incidentes
                elif adjust_lower_strip_underscore(data_type) in ['flooding_data']:
                    medicao = banco['incident']
                else:
                    return False
                medicao.insert_many(idataset)
                client.close()

        return True

    return False
