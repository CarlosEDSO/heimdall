# Heimdall 
    Coletor de dados publicos:
    Medições das estações meteorológicas no site da CGESP 
    Registros de alagamentos no site da CGESP 
    https://www.cgesp.org/v3/

```
    Status: Desenvolvimento
```

### Tecnologias:
* Python 3.6.1
 > * [Beautifulsoup4] : 4.6
 > * [Pymongo] : 3.6
 > * [Dnspython] : 1.14
 > * [Argparse] : 1.4
 > * [Dateutil] : 2.6
 > * [Requests] : 2.14


### Instalação

Clone o projeto em sua maquina

    $ git clone git@github.com:CarlosEDSO/heimdall.git

##### Crie um ambiente virtual para instalar as bibliotecas e executar o codigo
Recomendo utilizar o [Anaconda] mas pode ser outra ferramenta para criar seu ambiente virtual

    $ wget -c  http://repo.continuum.io/archive/Anaconda3-5.0.1-Linux-x86_64.sh
    $ bash Anaconda3-5.0.1-Linux-x86_64.sh
    $ source .bashrc
    $ conda create --name venv python==3.6.*


##### Ative o ambiente virtual e instale as bibliotecas do projeto

    $ source activate venv
    (venv) $ cd heimdall/
    (venv) $ pip install -r requirements.txt

### Utilizando o Heilmdall

##### service.py
O *service* e responsável por entregar as funcionalidades desenvolvidas, o arquivo
esta na raiz do projeto. Utilize o parâmetro -h ou --help para descobrir as opções:

    (venv) $ python service.py --help
    
##### Exemplos:
    (venv) $ python service.py --configure heimdall/configureflooding.json --dates 20160101 20160106
    (venv) $ python service.py --export flooding_data --dates 20160101 20160106

##### --configure
O parâmetro permite passar um arquivo de configuração que 
define a rodada, porem se o parâmetro não for utilizado 
sera usada a configuração padrão.

    (venv) $ python service.py --configure heimdall/configure.json

##### --dates
Data Inicial e Data Final da busca dos dados históricos 
(apenas para registros de alagamentos no momento).

    (venv) $ python service.py --dates YYYYMMDD YYYYMMDD
    (venv) $ python service.py --dates 20160101 20160106

##### --parallel && -processes_number
Data Inicial e Data Final da busca dos dados históricos 
(apenas para registros de alagamentos no momento).

    (venv) $ python service.py --parallel --processes_number 2

##### --export
Informe o tipo dos dados para exportar em um arquivo csv, 
adicione um periodo com o paramentro --dates

* Tipo de dados: 
    + flooding_data (Registros de alagamentos)
    + weather_station_data (Dados das estações meteorológicas)

Utilizando esse parâmetro o arquivo informado no parâmetro --configure sera ignorado!

    (venv) $ python service.py --export flooding_data --dates 20160101 20160106


### Tag das Mensagens:
    [I] -> Informacao
    [A] -> Aviso/Alerta
    [E] -> Erro


[Anaconda]: <https://anaconda.org/anaconda/python>
[Virtualenv]: <https://pypi.python.org/pypi/virtualenv>
[Argparse]: <https://docs.python.org/2/howto/argparse.html>
[Dateutil]: <https://dateutil.readthedocs.io/en/stable/>
[Requests]: <http://docs.python-requests.org/en/master/>
[Beautifulsoup4]: <https://pypi.python.org/pypi/beautifulsoup4>
[Pymongo]: <https://api.mongodb.com/python/current/>
[Dnspython]: <http://www.dnspython.org/>