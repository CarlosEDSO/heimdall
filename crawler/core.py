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
import os
import re
import ssl
import urllib.error
from datetime import datetime
from urllib.request import Request, urlopen

import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse

from heimdall.utils import adjust_lower_strip_underscore


def load_data_pag(url, verbose=False):
    '''
    
    :param url: str 
    :return: bs4.BeautifulSoup
    '''

    if verbose:
        print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.load_data_pag >> URL @ {_url}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            _url=url if not isinstance(url, Request) else url.get_full_url()
        ))

    regex = re.compile(r'[\n\r\t]')

    try:
        result = requests.get(url)
        return BeautifulSoup(result.text, 'html.parser')
    except:
        try:
            result = urlopen(url).read().decode('utf8')
            return BeautifulSoup(regex.sub("", result), 'html.parser')
        except urllib.error.HTTPError as e:
            print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.load_data_pag >> Error @ {e}'.format(
                dt=datetime.now(),
                pid=os.getpid(),
                e=e
            ))

    return BeautifulSoup("", 'html.parser')


def get_stations(configure: dict, verbose=False):
    '''
    
    :param configure: dict
    :param verbose: bool
    :return: list 
    '''

    if adjust_lower_strip_underscore(configure['source_data']) == 'cgesp':
        try:
            get_id = lambda item: re.compile(r'[estacao.jsp?POSTO=]').sub('', item)

            result = load_data_pag(url=configure['url_stations'], verbose=verbose)

            return [{'id': get_id(item.get('href')), 'name': item.get_text()} for item in
                    result.find_all(target='frm-estacoes')]
        except Exception as e:
            print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_stations >> '
                  'Error in searching the stations CGESP @ {e}'.format(
                dt=datetime.now(),
                pid=os.getpid(),
                e=e
            ))

    return list()


def get_weather_station_data(configure: dict, verbose=False):
    '''
    
    :param configure: dict 
    :param verbose: bool
    :return: list 
    '''

    if adjust_lower_strip_underscore(configure['source_data']) == 'cgesp':
        # try:
        url = Request(url=configure['url_data'])
        # É necessario inserir uma "referencia" para que durante a requisição
        # o site entenda que você não acessou diretamente a URL, no caso 'http://www.saisp.br/'
        url.add_header('REFERER', 'http://www.saisp.br/')
        result = load_data_pag(url=url, verbose=verbose).find(id='tbTelemBody')
        result = result.find_all('tr')

        if result:
            result = [item.find('td').get_text() for item in result]
            split_size = int(len(result) / 25)

            if split_size == 8:
                keys = ['data_medicao', 'precipitacao', 'velocidade_vento', 'direcao_vento', 'temperatura',
                        'umidade_relativa', 'pressao', 'sensacao_termica']
            elif split_size == 7:
                keys = ['data_medicao', 'precipitacao', 'velocidade_vento', 'direcao_vento', 'temperatura',
                        'umidade_relativa',
                        'pressao']
            elif split_size == 5:
                keys = ['data_medicao', 'precipitacao', 'temperatura', 'umidade_relativa', 'pressao']
            else:
                print('[A.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_weather_station_data >> '
                      'Could not read table @ {url}'.format(
                    dt=datetime.now(),
                    pid=os.getpid(),
                    url=configure['url_data']
                ))
                return list()

            try:
                result = [dict(zip(keys, result[i:i + split_size])) for i in range(0, len(result), split_size)]
            except Exception as e:
                print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_weather_station_data >> '
                      'Unexpected error @ {url} @ {e}'.format(
                    dt=datetime.now(),
                    pid=os.getpid(),
                    e=e,
                    url=configure['url_data']
                ))

            for index, value in enumerate(result):
                result[index]['data_medicao'] = parse(result[index]['data_medicao'])

            return result
        else:
            print('[A.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_weather_station_data >> '
                  'No data found @ {url}'.format(
                dt=datetime.now(),
                pid=os.getpid(),
                url=configure['url_data']
            ))

    return list()


def get_data(configure, verbose=False):
    '''
    
    :param url: str
    :param verbose: bool 
    :return: list
    '''

    if adjust_lower_strip_underscore(configure['data_type']) == 'weather_station_data':
        return get_weather_station_data(configure=configure, verbose=verbose)
    elif adjust_lower_strip_underscore(configure['data_type']) == 'flooding_data':
        return get_flooding_data(configure=configure, verbose=verbose)

    return list()


def get_flooding_data(configure, verbose=False):
    '''
    Alagamento
    :return: list
    '''

    if adjust_lower_strip_underscore(configure['source_data']) == 'cgesp':
        try:
            _data = list()
            for procdate in configure['processing_dates']:
                _url = copy.deepcopy(configure['url_data'])
                _url = _url.format(procdate=procdate)
                result = load_data_pag(url=_url, verbose=verbose)

                # Buscando os bairros
                for _bairro in result.find_all("table", class_="tb-pontos-de-alagamentos"):

                    bairro = _bairro.find("td", class_="bairro arial-bairros-alag linha-pontilhada").contents[0]

                    # Tirando os espaços do nome do bairro
                    bairro = re.sub('\\r+\\n+\\t+\\s+', '', bairro)

                    # Buscando os dados de alagamento
                    for _localizacoes in _bairro.find_all("div", class_="ponto-de-alagamento"):
                        _localizacao = _localizacoes.find_all("li")

                        rua = str(_localizacao[2].contents[2]).strip()
                        referencia = str(_localizacao[4].contents[2].replace('Referência: ', '')).strip()
                        sentido = _localizacao[4].contents[0].replace('Sentido: ', '')
                        situacao = _localizacao[0].get('title').replace('Inativo ', '')

                        adjust_hour = lambda item: procdate.replace(hour=int(item.split(':')[0]),
                                                                    minute=int(item.split(':')[1]))
                        hora = re.findall('\d{2}:\d{2}', _localizacao[2].contents[0])
                        hora = list(map(adjust_hour, hora))

                        _data.append(dict(bairro=bairro, rua=rua, referencia=referencia, sentido=sentido,
                                          hora_inicial=hora[0], hora_termino=hora[1], situacao=situacao))

            return _data
        except Exception as e:
            print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_flooding_data >> '
                  'Error in searching the CGESP data @ {e}'.format(
                dt=datetime.now(),
                pid=os.getpid(),
                e=e
            ))

    return list()
