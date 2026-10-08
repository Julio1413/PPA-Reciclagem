import json
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import Ferramentas

print('='*20)
print('Módulo Ferramentas')

# Pasta padrão usada por este módulo e pelo Auth.py (sessão, arquivos locais etc.)

URL_SUPABASE = 'https://fcbtecufrukxbmtngktc.supabase.co'
CHAVE_SUPABASE = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZjYnRlY3VmcnVreGJtdG5na3RjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODk0MTM0NjEsImV4cCI6MjEwNDk4OTQ2MX0.kOKrOwwMGwMtLuC8APEO-pvJhUWJKcG9IKz58J0f3-E'  # anon/public key do projeto


def ObterCredenciais():
    if not URL_SUPABASE or not CHAVE_SUPABASE:
        return None, None
    return URL_SUPABASE, CHAVE_SUPABASE


def _headers(api_key):
    return {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def TestarConexao(tabela_teste="login"):
    """Retorna a lista de dados se as credenciais forem válidas, ou None em caso de erro."""
    url, key = ObterCredenciais()
    if not url or not key:
        return None
    try:
        r = requests.get(
            f"{url}/rest/v1/{tabela_teste}?limit=1",
            headers=_headers(key),
            timeout=30,
            verify=False,
        )
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print("ERRO TestarConexao:", e)
        return None


def LerTabela(nome_tabela, filtros=None):
    url, key = ObterCredenciais()
    if not url or not key:
        return None
    try:
        r = requests.get(
            f"{url}/rest/v1/{nome_tabela}",
            headers=_headers(key),
            params=filtros or {},
            timeout=30,
            verify=False,
        )
        return r.json() if r.status_code == 200 else None
    except Exception as e:
        print("ERRO LerTabela:", e)
        return None


def InserirLinha(nome_tabela, dados: dict):
    url, key = ObterCredenciais()
    if not url or not key:
        return None
    try:
        r = requests.post(
            f"{url}/rest/v1/{nome_tabela}",
            headers=_headers(key),
            data=json.dumps(dados),
            timeout=30,
            verify=False,
        )
        return True if r.status_code in (200, 201) else None
    except Exception as e:
        print("ERRO InserirLinha:", e)
        return None


def AtualizarLinha(nome_tabela, filtros: dict, novos_dados: dict):
    """filtros: {"id": "eq.1"} ou {"email": "eq.teste@gmail.com"}"""
    url, key = ObterCredenciais()
    if not url or not key:
        return None
    try:
        r = requests.patch(
            f"{url}/rest/v1/{nome_tabela}",
            headers=_headers(key),
            params=filtros,
            data=json.dumps(novos_dados),
            timeout=30,
            verify=False,
        )
        return True if r.status_code in (200, 204) else None
    except Exception as e:
        print("ERRO AtualizarLinha:", e)
        return None


def ExcluirLinha(nome_tabela, filtros: dict):
    url, key = ObterCredenciais()
    if not url or not key:
        return None
    try:
        r = requests.delete(
            f"{url}/rest/v1/{nome_tabela}",
            headers=_headers(key),
            params=filtros,
            timeout=30,
            verify=False,
        )
        return True if r.status_code in (200, 204) else None
    except Exception as e:
        print("ERRO ExcluirLinha:", e)
        return None


def InserirLog(mensagem: str):
    from datetime import datetime
    log = {
        "mensagem": mensagem,
        "registrado_em": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "autor": Ferramentas.ler_arquivo('NOME.txt'),
    }
    InserirLinha('logs', log)
    return log
