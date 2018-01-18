# -*- coding: utf-8 -*-

'''
    File name: service.py
    Python Version: 3.6.1
'''

# Tag das Mensagens:
# [I] -> Informacao
# [A] -> Aviso/Alerta
# [E] -> Erro

__author__ = 'Carlos Oliveira'
__version__ = '0.1'
__email__ = 'carlos.oliveira226@gmail.com'
__status__ = "Development"

import sys
import os
import json
from datetime import datetime

import argparse

import controller
from heimdall.settings import BASE_DIR

parser = argparse.ArgumentParser(description='''Plataforma de coleta de dados''',
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-v", "--verbose", action='store_true', dest='verbose', help="Verbose", default=False)
parser.add_argument("-procdate", type=str, dest='procdate', help="Data de Processamento", default=None)
parser.add_argument("-configure", type=str, dest='configure', help="Arquivo de configuração",
                    default='{base_dir}/heimdall/configure.json'.format(base_dir=BASE_DIR))
args = parser.parse_args()

if __name__ == "__main__":
    print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] Inicio - {path}'.format(dt=datetime.now(), pid=os.getpid(), path=sys.argv[0]))

    controller.run(configure=json.loads(open(args.configure).read()), procdate=args.procdate, verbose=args.verbose)

    print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] Fim - {path}'.format(dt=datetime.now(), pid=os.getpid(), path=sys.argv[0]))
    sys.exit(0)
