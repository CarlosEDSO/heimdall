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
from urllib.request import Request, urlopen
import urllib.error
from datetime import datetime

from bs4 import BeautifulSoup


def load_data_pag(url):
    '''
    
    :param url: str 
    :return: bs4.BeautifulSoup
    '''
    regex = re.compile(r'[\n\r\t]')

    try:
        result = urlopen(url, context=ssl.SSLContext()).read().decode('utf8')
    except urllib.error.HTTPError as e:
        print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_stations >> Error @ {e}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            e=e
        ))
        return BeautifulSoup("", 'html.parser')

    result = BeautifulSoup(regex.sub("", result), 'html.parser')
    return result


def get_stations(url, verbose=False):
    '''
    
    :param verbose: bool 
    :return: list
    '''

    get_id = lambda item: re.compile(r'[estacao.jsp?POSTO=]').sub('', item)

    if verbose:
        print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_stations >> URL @ {_url}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            _url=url
        ))

    result = load_data_pag(url=url)

    return [{'id': get_id(item.get('href')), 'name': item.get_text()} for item in
            result.find_all(target='frm-estacoes')]


def get_data(url, verbose=False):
    '''
    
    :param url: str
    :param verbose: bool 
    :return: 
    '''

    if verbose:
        print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_data >> URL @ {_url}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            _url=url
        ))

    url = Request(url=url)
    # É necessario inserir uma "referencia" para que durante a requisição
    # o site entenda que você não acessou diretamente a URL, no caso 'http://www.saisp.br/'
    url.add_header('REFERER', 'http://www.saisp.br/')
    result = load_data_pag(url=url).find(id='tbTelemBody')
    result = result.find_all('tr')

    result = [item.find('td').get_text() for item in result]
    split_size = 7
    keys = ['data_medicao', 'precipitacao', 'velocidade_vento', 'direcao_vento', 'temperatura', 'umidade_relativa',
            'pressao']

    return [dict(zip(keys, result[i:i + split_size])) for i in range(0, len(result), split_size)]
