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

from crawler import get_stations, get_data


def run(configure, verbose=False) -> bool:
    '''
    
    :param configure: 
    :param procdate: 
    :param verbose: 
    :return: 
    '''

    result, stations = list(), list()

    _url_station = 'https://www.cgesp.org/v3/estacoes-meteorologicas.jsp'
    _url_data = 'https://www.saisp.br/geral/processo_cge.jsp?WHICHCHANNEL={station_id}'
    stations = get_stations(url=_url_station, verbose=verbose)

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
                
            _url = str(_url_data).format(station_id=station['id'])
            station_info = dict(station_id=station['id'], station_name=station['name'])

            for index, row in enumerate(get_data(url=_url, verbose=verbose)):
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
