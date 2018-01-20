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
import ssl
import re
import copy
from urllib.request import Request, urlopen
import urllib.error
from datetime import datetime

import requests
from bs4 import BeautifulSoup


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
            result = urlopen(url, context=ssl.SSLContext()).read().decode('utf8')
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

    if str(configure['source_data']).lower() == 'cgesp':
        get_id = lambda item: re.compile(r'[estacao.jsp?POSTO=]').sub('', item)

        result = load_data_pag(url=configure['url_stations'], verbose=verbose)

        return [{'id': get_id(item.get('href')), 'name': item.get_text()} for item in
                result.find_all(target='frm-estacoes')]

    return list()


def get_weather_station_data(configure: dict, verbose=False):
    '''
    
    :param configure: dict 
    :param verbose: bool
    :return: list 
    '''

    if str(configure['source_data']).lower() == 'cgesp':
        url = Request(url=configure['url_data'])
        # É necessario inserir uma "referencia" para que durante a requisição
        # o site entenda que você não acessou diretamente a URL, no caso 'http://www.saisp.br/'
        url.add_header('REFERER', 'http://www.saisp.br/')
        result = load_data_pag(url=url, verbose=verbose).find(id='tbTelemBody')
        result = result.find_all('tr')

        result = [item.find('td').get_text() for item in result]
        split_size = 7
        keys = ['data_medicao', 'precipitacao', 'velocidade_vento', 'direcao_vento', 'temperatura', 'umidade_relativa',
                'pressao']

        return [dict(zip(keys, result[i:i + split_size])) for i in range(0, len(result), split_size)]

    return list()


def get_data(configure, verbose=False):
    '''
    
    :param url: str
    :param verbose: bool 
    :return: list
    '''

    if str(configure['data_type']).lower().replace(' ', '_') == 'weather_station_data':
        return get_weather_station_data(configure=configure, verbose=verbose)
    elif str(configure['data_type']).lower().replace(' ', '_') == 'flooding_data':
        return get_flooding_data(configure=configure, verbose=verbose)

    return list()


def get_flooding_data(configure, verbose=False):
    '''
    Alagamento
    :return: list
    '''

    if str(configure['source_data']).lower() == 'cgesp':
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

    return list()
