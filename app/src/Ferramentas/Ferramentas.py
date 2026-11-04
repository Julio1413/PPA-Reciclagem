import flet as ft, os, platform
import json
# padding geral da ui

print('='*20)
print('Módulo Ferramentas')

_Pasta_Global = None
def DefinirPasta():
    global _Pasta_Global
    #Definir a pasta global
    sistema = platform.system()
    if sistema == "Windows":
        _Pasta_Global = r'C:\404Studios\622-Reciclagem'
    elif "ANDROID_BOOTLOGO" in os.environ or (sistema == "Linux" and "arm" in platform.uname().machine):
        _Pasta_Global = os.getenv("FLET_APP_STORAGE_DATA")
    elif sistema == "Linux":
        _Pasta_Global = os.path.expanduser("~/404Studios/622-Reciclagem")
    else:
        _Pasta_Global = r'C:\404Studios\622-Reciclagem'
    return _Pasta_Global


def PastaGlobal():
    return _Pasta_Global


def DefinirPastaGlobal(pasta):
    global _Pasta_Global
    _Pasta_Global = pasta
    if pasta:
        os.makedirs(pasta, exist_ok=True)


def CaminhoArquivo(nome: str):
    return os.path.join(_Pasta_Global, nome) if _Pasta_Global else None



def CriarArquivo(nome:str,conteudo:str,metodo='w'):
    if _Pasta_Global: #local
        with open(os.path.join(_Pasta_Global,nome), metodo, encoding="utf-8") as f:
            f.write(conteudo)

        
def LerArquivo(nome: str, default=None):
    if _Pasta_Global:
        caminho = os.path.join(_Pasta_Global, nome)
        if os.path.exists(caminho):
            with open(caminho, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return default

def LerJson(nome:str):
    return json.loads(LerArquivo(nome))


def DeletarArquivo(nome:str):
    if _Pasta_Global:
        if os.path.exists(os.path.join(_Pasta_Global,nome)):
            os.remove(os.path.join(_Pasta_Global,nome))

def DeletarArquivos(arquivos=[]):
    if _Pasta_Global:
        for arquivo in arquivos:
            if ArquivoExiste(arquivo):
                DeletarArquivo(arquivo)

def ArquivoExiste(nome: str):
    if _Pasta_Global:
        return os.path.exists(os.path.join(_Pasta_Global, nome))
    return False

def ArquivosExistem(arquivos=[]):
    if _Pasta_Global:
        for arquivo in arquivos:
            if not ArquivoExiste(arquivo):
                return False
        return True


def CalcularDistancia(coord1, coord2):
    import math
    """
    Recebe duas coordenadas (latitude, longitude)
    e retorna a distância entre elas em quilômetros.
    """
    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    print(f'Distancia entre {coord1} e {coord2}: {6371 * c:.2f} km')
    return 6371 * c
