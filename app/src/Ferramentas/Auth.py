import json
import os
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from Ferramentas.Supabase import ObterCredenciais
from Ferramentas import Ferramentas

ARQUIVO_SESSAO = os.path.join(Ferramentas._Pasta_Global, "sessao.json")


def _headers_auth(api_key):
    return {
        "apikey": api_key,
        "Content-Type": "application/json",
    }


def CadastrarUsuario(email, senha, nome=None, telefone=None):
    """
    nome/telefone são opcionais e vão como metadata do usuário
    (auth.users.raw_user_meta_data), não como o campo nativo "phone" do
    Supabase Auth. Motivo: o campo nativo "phone" ativa o fluxo de
    verificação por SMS, que exige um provedor (Twilio etc.) configurado
    no projeto — sem isso, o cadastro falharia. Como você só quer guardar
    o telefone como dado de perfil, ele entra em "data" junto com o nome.
    """
    url, key = ObterCredenciais()
    if not url or not key:
        return None
    try:
        payload = {"email": email, "password": senha}

        metadata = {}
        if nome:
            # "full_name"/"name" são as chaves que o Supabase Studio usa
            # para preencher a coluna "Display Name" da lista de usuários.
            metadata["full_name"] = nome
            metadata["name"] = nome
        if telefone:
            metadata["phone"] = telefone
        if metadata:
            payload["data"] = metadata

        r = requests.post(
            f"{url}/auth/v1/signup",
            headers=_headers_auth(key),
            data=json.dumps(payload),
            timeout=30,
            verify=False,
        )
        if r.status_code not in (200, 201):
            print(f"ERRO CadastrarUsuario: status {r.status_code} - {r.text}")
            return None

        dados = r.json()
        if "access_token" in dados:
            # Só existe sessão imediata se a confirmação de e-mail
            # estiver desativada no projeto Supabase.
            _SalvarSessao(dados)
        return dados
    except Exception as e:
        print("ERRO CadastrarUsuario:", e)
        return None


def LoginUsuario(email, senha):
    url, key = ObterCredenciais()
    if not url or not key:
        return None
    try:
        r = requests.post(
            f"{url}/auth/v1/token?grant_type=password",
            headers=_headers_auth(key),
            data=json.dumps({"email": email, "password": senha}),
            timeout=30,
            verify=False,
        )
        if r.status_code != 200:
            print(f"ERRO LoginUsuario: status {r.status_code} - {r.text}")
            return None

        dados = r.json()
        _SalvarSessao(dados)
        return dados
    except Exception as e:
        print("ERRO LoginUsuario:", e)
        return None


def AtualizarPerfil(nome=None, telefone=None):
    """
    Atualiza nome/telefone (metadata) do usuário atualmente logado.
    Requer sessão salva (ObterSessao() precisa retornar algo).
    """
    url, key = ObterCredenciais()
    sessao = ObterSessao()
    if not url or not key or not sessao or not sessao.get("access_token"):
        print("ERRO AtualizarPerfil: nenhuma sessão ativa")
        return None

    metadata = {}
    if nome:
        metadata["full_name"] = nome
        metadata["name"] = nome
    if telefone:
        metadata["phone"] = telefone
    if not metadata:
        return None

    try:
        r = requests.put(
            f"{url}/auth/v1/user",
            headers={**_headers_auth(key), "Authorization": f"Bearer {sessao['access_token']}"},
            data=json.dumps({"data": metadata}),
            timeout=30,
            verify=False,
        )
        if r.status_code != 200:
            print(f"ERRO AtualizarPerfil: status {r.status_code} - {r.text}")
            return None

        dados = r.json()
        # a sessão salva localmente também guarda uma cópia do usuário;
        # atualizamos essa cópia pra refletir o novo nome/telefone.
        sessao["user"] = dados
        _SalvarSessao(sessao)
        return dados
    except Exception as e:
        print("ERRO AtualizarPerfil:", e)
        return None


def LogoutUsuario():
    url, key = ObterCredenciais()
    sessao = ObterSessao()

    if url and key and sessao and sessao.get("access_token"):
        try:
            requests.post(
                f"{url}/auth/v1/logout",
                headers={**_headers_auth(key), "Authorization": f"Bearer {sessao['access_token']}"},
                timeout=30,
                verify=False,
            )
        except Exception as e:
            print("ERRO LogoutUsuario:", e)

    _LimparSessao()


def ObterSessao():
    """Retorna a última sessão salva localmente (ou None se nunca logou / fez logout)."""
    if not os.path.exists(ARQUIVO_SESSAO):
        return None
    try:
        with open(ARQUIVO_SESSAO, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("ERRO ObterSessao:", e)
        return None


def _SalvarSessao(dados: dict):
    os.makedirs(Ferramentas._Pasta_Global, exist_ok=True)
    with open(ARQUIVO_SESSAO, "w", encoding="utf-8") as f:
        json.dump(dados, f)


def _LimparSessao():
    if os.path.exists(ARQUIVO_SESSAO):
        os.remove(ARQUIVO_SESSAO)