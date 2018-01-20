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
import copy
import multiprocessing
from datetime import datetime

from crawler import get_stations, get_data


def run(configure, parallel=False, processes_number=int(multiprocessing.cpu_count() / 2), verbose=False):
    '''
    
    :param configure: 
    :param verbose: 
    :return: 
    '''
    if parallel:
        pool = multiprocessing.Pool(processes=processes_number)
        pool.map(run_task, configure)
    else:
        for task in configure:
            run_task(configure=task, verbose=verbose)


def run_task(configure, verbose=False) -> bool:
    '''
    
    :param configure: 
    :param procdate: 
    :param verbose: 
    :return: 
    '''

    result, stations = list(), list()

    stations = get_stations(configure=configure, verbose=verbose)

    if stations:
        for station in stations:
            if verbose:
                print(
                    '[I.{dt:%Y%m%d%H%M}][PID.{pid}] controller.run >> Station @ id:{station_id:12} name:{station_name}'.format(
                        dt=datetime.now(),
                        pid=os.getpid(),
                        station_id=station['id'],
                        station_name=station['name']
                    ))

            _configure = copy.deepcopy(configure)
            _configure['url_data'] = str(_configure['url_data']).format(station_id=station['id'])

            station_info = dict(station_id=station['id'], station_name=station['name'])

            for index, row in enumerate(get_data(configure=_configure, verbose=verbose)):
                row.update(station_info)
                result.append(row)
    else:
        print('[A.{dt:%Y%m%d%H%M}][PID.{pid}] controller.run >> No stations found'.format(
            dt=datetime.now(),
            pid=os.getpid(),
        ))

    # Imprimindo os resultados
    for index, row in enumerate(result):
        print(index, row)

    return True
