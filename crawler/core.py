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
from datetime import datetime, timedelta

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
            _url=url
        ))

    regex = re.compile(r'[\n\r\t]')

    try:
        result = urlopen(url, context=ssl.SSLContext()).read().decode('utf8')
    except urllib.error.HTTPError as e:
        print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.load_data_pag >> Error @ {e}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            e=e
        ))
        return BeautifulSoup("", 'html.parser')

    result = BeautifulSoup(regex.sub("", result), 'html.parser')
    return result


def get_stations(configure, verbose=False):
    '''
    
    :param verbose: bool 
    :return: list
    '''

    if str(configure['source_data']).lower() == 'cgesp':
        get_id = lambda item: re.compile(r'[estacao.jsp?POSTO=]').sub('', item)

        result = load_data_pag(url=configure['url_stations'], verbose=verbose)

        return [{'id': get_id(item.get('href')), 'name': item.get_text()} for item in
                result.find_all(target='frm-estacoes')]

    return list()


def get_weather_station_data(configure, verbose=False):
    '''
    
    :return: 
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
    :return: 
    '''

    if str(configure['data_type']).lower() == 'weather_station_data':
        return get_weather_station_data(configure=configure, verbose=verbose)

    return list()


def alagamento(configure, verbose=False):
    '''
    
    :return: 
    '''

    # Alagamento
    _url = 'https://www.cgesp.org/v3/alagamentos.jsp?dataBusca={idate}&enviaBusca=Buscar'
    #
    # for i in range(0, 3):
    #     _idate = start_date + timedelta(days=i)
    #     print(_idate)
    #     response = requests.get(_url.format(idate=_idate.strftime('%d/%m/%Y'), safe=''))
    #     _soup = BeautifulSoup(response.text, 'html.parser')
    #     for bairro in _soup.find_all("table", class_="tb-pontos-de-alagamentos"):
    #         sub = bairro.find("td", class_="bairro arial-bairros-alag linha-pontilhada").contents[0]
    #         sub = re.sub('\\r+\\n+\\t+\\s+', '', sub)
    #         print(f'\n{sub} :')
    #         for _localizacoes in bairro.find_all("div", class_="ponto-de-alagamento"):
    #             _localizacao = _localizacoes.find_all("li")
    #
    #             rua = str(_localizacao[2].contents[2]).strip()
    #             reference = str(_localizacao[4].contents[2].replace('Referência: ', '')).strip()
    #             sentido = _localizacao[4].contents[0].replace('Sentido: ', '')
    #
    #             hora = re.findall('\d{2}:\d{2}', _localizacao[2].contents[0])
    #
    #             print(rua, reference, sentido, hora)