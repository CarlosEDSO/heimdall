# -*- coding: utf-8 -*-

'''
    File name: core.py
    Python Version: 3.6.1
'''

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

import copy
import multiprocessing
import os
from datetime import datetime, timedelta

from dateutil.parser import parse

from crawler import get_stations, get_data
from datahub import insert_data, export_data
from heimdall.settings import DEFAULT_OUTPUT_PATH
from heimdall.utils import adjust_lower_strip_underscore as adjust_lsu


def run(boot_settings, processing_dates=None, parallel=False, processes_number=int(multiprocessing.cpu_count() / 2),
        verbose=False):
    '''
    
    :param configure: dict
    :param parallel: bool
    :param processes_number: int 
    :param verbose: bool
    :return: 
    '''

    if not os.path.exists(DEFAULT_OUTPUT_PATH):
        os.makedirs(DEFAULT_OUTPUT_PATH)

    result = list()

    # Pre Processamento
    for it in range(len(boot_settings)):
        boot_settings[it].update({'processing_dates': processing_dates})
        boot_settings[it].update({'verbose': verbose})

    # Processamento
    if parallel:
        pool = multiprocessing.Pool(processes=int(processes_number))
        result = pool.map(run_task, boot_settings)
    else:
        for configure in boot_settings:
            result.append(run_task(configure=configure))

    # Report
    if verbose:
        for _result, configure in zip(result, boot_settings):
            print(
                '[I.{dt:%Y%m%d%H%M}][PID.{pid}] controller.run >> '
                'Processed : {_result} | Configuration : {configure}'.format(
                    dt=datetime.now(),
                    pid=os.getpid(),
                    _result=_result,
                    configure=configure
                )
            )


def run_task(configure) -> bool:
    '''
    
    :param configure: dict
    :return: 
    '''
    try:
        if adjust_lsu(configure['process_type']) == 'collect_data':
            if adjust_lsu(configure['data_type']) == 'weather_station_data':
                return _run_task_weather_station(configure=configure, verbose=configure['verbose'])
            elif adjust_lsu(configure['data_type']) == 'flooding_data':
                return _run_task_flooding_data(configure=configure, verbose=configure['verbose'])
        elif adjust_lsu(configure['process_type'] == 'export_data'):
            return _run_task_export_data(configure=configure, verbose=configure['verbose'])
    except Exception as e:
        print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] controller.run_task >> Unexpected error @ {configure}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            configure=configure
        ))


def _run_task_export_data(configure, verbose=False) -> bool:
    '''
    
    :param configure: dict 
    :param verbose: bool
    :return: bool
    '''

    if configure['processing_dates']:
        start, end = configure['processing_dates']
        start, end = parse(start), parse(end)
    else:
        start, end = datetime.today() - timedelta(days=1), datetime.today()
        start, end = start.replace(hour=0, minute=0), end.replace(hour=23, minute=59)

    export_data(data_type=configure['data_type'], start_date=start, end_date=end, verbose=verbose)


def _run_task_weather_station(configure, verbose=False) -> bool:
    '''

    :param configure: 
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
        return False

    if result:
        if 'store_data' in configure.keys():
            store_data = configure['store_data']
            if 'database' in store_data:
                success = insert_data(idataset=result, data_type='weather_station_data',
                                      verbose=verbose)
                if success:
                    print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] controller._run_task_weather_station >> '
                          'Inserted into database'.format(
                        dt=datetime.now(),
                        pid=os.getpid(),
                    ))
    else:
        print('[A.{dt:%Y%m%d%H%M}][PID.{pid}] controller._run_task_weather_station >> '
              'No data found'.format(
            dt=datetime.now(),
            pid=os.getpid(),
        ))
        return False

    return True


def _run_task_flooding_data(configure, verbose=False) -> bool:
    '''

    :param configure: 
    :param verbose: 
    :return: 
    '''

    result = list()

    if configure['processing_dates']:
        start, end = configure['processing_dates']
        start, end = parse(start), parse(end)
    else:
        start, end = datetime.today() - timedelta(days=1), datetime.today()

    configure['processing_dates'] = [start + timedelta(days=i) for i in range(0, abs((start - end).days - 1))]

    result = get_data(configure, verbose=verbose)

    if result:
        if 'store_data' in configure.keys():
            store_data = configure['store_data']
            if 'database' in store_data:
                success = insert_data(idataset=result, data_type='flooding_data', verbose=verbose)
                if success:
                    print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] controller._run_task_flooding_data >> '
                          'Inserted into database '.format(
                        dt=datetime.now(),
                        pid=os.getpid(),
                    ))
    else:
        print('[A.{dt:%Y%m%d%H%M}][PID.{pid}] controller._run_task_flooding_data >> '
              'No data found '.format(
            dt=datetime.now(),
            pid=os.getpid(),
        ))
        return False

    return True
