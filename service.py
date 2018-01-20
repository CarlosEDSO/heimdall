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
import multiprocessing
from datetime import datetime

import argparse

import controller
from heimdall.settings import BASE_DIR

parser = argparse.ArgumentParser(description='''Plataforma de coleta de dados''',
                                 formatter_class=argparse.RawTextHelpFormatter)

parser.add_argument("-v", "--verbose", action='store_true', dest='verbose', help="Verbose", default=False)
parser.add_argument("-configure", type=str, dest='configure', help="Arquivo de configuração",
                    default='{base_dir}/heimdall/configure.json'.format(base_dir=BASE_DIR))
parser.add_argument("-dates", type=str, nargs=2, dest='dates',
                    help="Data Inicial e Data Final da busca dos dados historicos\n "
                         "(apenas para registros de alagamentos). \n"
                         "Formatos sugerido para a data: YYYYMMDD YYYYMMDD\n"
                         "(AnoMêsDia)",
                    default=None)
parser.add_argument("-parallel", action='store_true', dest='parallel', help="Parallel", default=False)

processes_number = int(multiprocessing.cpu_count() / 2)
parser.add_argument("-processes_number", type=int, dest='processes_number',
                    help="Numero de processos para o caso do parametro -parallel ser utilizado.\n"
                         "Padrão: Metade do numero de processadores da maquina {0}".format(processes_number)
                    , default=processes_number)

args = parser.parse_args()

if __name__ == "__main__":
    print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] Inicio - {path}'.format(dt=datetime.now(), pid=os.getpid(), path=sys.argv[0]))

    controller.run(boot_settings=json.loads(open(args.configure).read()), processing_dates=args.dates,
                   parallel=args.parallel, processes_number=args.processes_number, verbose=args.verbose)

    print('[I.{dt:%Y%m%d%H%M}][PID.{pid}] Fim - {path}'.format(dt=datetime.now(), pid=os.getpid(), path=sys.argv[0]))
    sys.exit(0)
