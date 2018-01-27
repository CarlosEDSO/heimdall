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

import pandas
import pymongo.errors
from pymongo import MongoClient

from heimdall.settings import DATABASES, COMMIT_DATABASE, ENVIRONMENT_DATABASE, DEFAULT_OUTPUT_PATH
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


def insert_data(idataset, data_type, verbose=False):
    '''
    
    :param idataset: list
    :param data_type: str
    :param name_database: str 
    :param verbose: bool
    :return: 
    '''

    if ENVIRONMENT_DATABASE in DATABASES.keys() and COMMIT_DATABASE:
        infodb = DATABASES[ENVIRONMENT_DATABASE]
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


def export_data(data_type: str, start_date: datetime, end_date: datetime, verbose=False):
    '''
    
    :param data_type: str
    :param name_database: str 
    :param start_date: datetime.datetime 
    :param end_date: datetime.datetime
    :param verbose: bool
    :return: 
    '''
    if ENVIRONMENT_DATABASE in DATABASES.keys() and COMMIT_DATABASE:
        infodb = DATABASES[ENVIRONMENT_DATABASE]
        if adjust_lower_strip_underscore(infodb['type']) == 'mongodb':
            client = get_connection(info=infodb)
            if client:
                banco = client[infodb['database']]
                if adjust_lower_strip_underscore(data_type) == 'weather_station_data':
                    medicao = banco['weather_data']
                    result = medicao.find({'data_medicao': {'$lt': start_date, '$gte': end_date}})
                    file_name = '{0}/{1:%Y%m%d}_{2}_{3:%Y%m%d}_{4:%Y%m%d}.csv'.format(DEFAULT_OUTPUT_PATH, datetime.today(),
                                                                                  data_type,
                                                                                  start_date,
                                                                                  end_date)
                    write_csv(file_name=file_name, idataset=result, verbose=verbose)
                    return True
                # Pode vir a abranger outros tipos de incidentes
                elif adjust_lower_strip_underscore(data_type) in ['flooding_data']:
                    medicao = banco['incident']
                    result = medicao.find({'hora_inicial': {'$gte': start_date, '$lte': end_date}})
                    file_name = '{0}/{1:%Y%m%d}_{2}_{3:%Y%m%d}_{4:%Y%m%d}.csv'.format(DEFAULT_OUTPUT_PATH, datetime.today(),
                                                                                  data_type,
                                                                                  start_date,
                                                                                  end_date)
                    write_csv(file_name=file_name, idataset=result, verbose=verbose)
                    return True

    print('[A.{dt:%Y%m%d%H%M}][PID.{pid}] datahub.export_data >> '
          'Data not found '.format(
        dt=datetime.now(),
        pid=os.getpid(),
    ))

    return False


def write_csv(file_name, idataset, verbose=False):
    '''
    
    :param idataset: 
    :param verbose: 
    :return: 
    '''

    try:
        idataset = pandas.DataFrame(list(idataset))
        if '_id' in list(idataset):
            del idataset['_id']

        idataset.to_csv(file_name, index=False)
        print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] datahub.write_csv >> '
              '{f} '.format(
            dt=datetime.now(),
            pid=os.getpid(),
            f=file_name
        ))
    except Exception as e:
        print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] datahub.write_csv >> '
              '{e} '.format(
            dt=datetime.now(),
            pid=os.getpid(),
            e=e
        ))
