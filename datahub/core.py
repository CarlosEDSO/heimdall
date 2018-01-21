# -*- coding: utf-8 -*-

'''
    File name: core.py
    Python Version: 3.6.1
'''

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro


from pymongo import MongoClient

from heimdall.settings import DATABASES
from heimdall.utils import adjust_lower_strip_underscore


def get_connection(info):
    if adjust_lower_strip_underscore(info['type']) == 'mongodb':
        return MongoClient(info['host'], username='heimdall',
                           password='Ddpr3iNDHy3z3vSw', ssl=True, authSource='admin')

    return None


def insert_data(idataset, data_type, name_database, verbose=False):
    '''
    
    :param idataset: 
    :param verbose: 
    :return: 
    '''

    if name_database in DATABASES.keys():
        infodb = DATABASES[name_database]
        if adjust_lower_strip_underscore(infodb['type']) == 'mongodb':
            client = get_connection(info=infodb)
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
