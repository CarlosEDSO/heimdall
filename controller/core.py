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

from crawler import get_stations


def run(configure, verbose=False) -> bool:
    '''
    
    :param configure: 
    :param procdate: 
    :param verbose: 
    :return: 
    '''

    result = get_stations(verbose=verbose)
    if result:
        for item in result:
            print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] controller.run >> Station @ id:{station_id:12} name:{station_name}'.format(
                dt=datetime.now(),
                pid=os.getpid(),
                station_id=item['id'],
                station_name=item['name']
            ))
    else:
        print('[A.{dt:%Y%m%d%H%M}][PID.{pid}] controller.run >> No stations found'.format(
            dt=datetime.now(),
            pid=os.getpid(),
        ))

    return True
