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
import re
import urllib.request as _request
import urllib.error
from datetime import datetime

from bs4 import BeautifulSoup


def get_stations(verbose=False):
    '''
    
    :param verbose: bool 
    :return: list
    '''
    regex = re.compile(r'[\n\r\t]')
    get_id = lambda item: re.compile(r'[estacao.jsp?POSTO=]').sub('', item)
    _url = 'https://www.cgesp.org/v3/estacoes-meteorologicas.jsp'

    if verbose:
        print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_stations >> URL @ {_url}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            _url=_url
        ))

    try:
        result = _request.urlopen(_url).read().decode('utf8')
    except urllib.error.HTTPError as e:
        print('[E.{dt:%Y%m%d%H%M}][PID.{pid}] crawler.get_stations >> Error @ {e}'.format(
            dt=datetime.now(),
            pid=os.getpid(),
            e=e
        ))
        return None

    result = BeautifulSoup(regex.sub("", result), 'html.parser')

    return [{'id': get_id(item.get('href')), 'name': item.get_text()} for item in
            result.find_all(target='frm-estacoes')]
