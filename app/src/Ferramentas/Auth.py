import json
import os
import requests
import urllib3

print('='*20)
print('Módulo Auth')


urllib3.disable_warnings(
    urllib3.exceptions.InsecureRequestWarning
)

from Ferramentas.Supabase import ObterCredenciais
from Ferramentas.Ferramentas import _Pasta_Global


# ============================================================
# ARQUIVOS
# ============================================================

ARQUIVO_SESSAO = os.path.join(
    _Pasta_Global,
    "sessao.json"
)

# Arquivo separado para os tokens.
# Não deve ser usado para guardar nome, e-mail ou outros dados.
ARQUIVO_TOKENS = os.path.join(
    _Pasta_Global,
    ".sessao_tokens.json"
)


# ============================================================
# CÓDIGOS DE RETORNO
# ============================================================

CADASTRO_OK = 0
EMAIL_JA_CADASTRADO = 1
ERRO_CADASTRO = 2


# ============================================================
# HEADERS
# ============================================================

def _headers_auth(api_key):
    return {
        "apikey": api_key,
        "Content-Type": "application/json",
    }


def _headers_autenticado(api_key, access_token):
    return {
        "apikey": api_key,
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }


# ============================================================
# CADASTRO
# ============================================================

def CadastrarUsuario(email, senha, nome):
    """
    Cadastra um novo usuário.

    Retorno:

        CADASTRO_OK
            0

        EMAIL_JA_CADASTRADO
            1

        ERRO_CADASTRO
            2
    """

    url, key = ObterCredenciais()

    if not url or not key:
        return ERRO_CADASTRO

    try:

        payload = {
            "email": email,
            "password": senha,
            "data": {
                "full_name": nome,
                "name": nome,
            }
        }

        r = requests.post(
            f"{url}/auth/v1/signup",
            headers=_headers_auth(key),
            data=json.dumps(payload),
            timeout=30,
            verify=False,
        )

        # ----------------------------------------------------
        # E-MAIL JÁ EXISTENTE
        # ----------------------------------------------------

        if r.status_code not in (200, 201):

            corpo = r.text.lower()

            if (
                "already registered" in corpo
                or "already exists" in corpo
                or "user_already_exists" in corpo
            ):
                return EMAIL_JA_CADASTRADO

            print(
                f"ERRO CadastrarUsuario: "
                f"status {r.status_code} - {r.text}"
            )

            return ERRO_CADASTRO

        dados = r.json()

        # Com confirmação de e-mail ativada, o Supabase pode
        # retornar identities vazio para um e-mail já cadastrado.
        if dados.get("identities") == []:
            return EMAIL_JA_CADASTRADO

        # ----------------------------------------------------
        # CADASTRO REALIZADO
        # ----------------------------------------------------

        if "access_token" in dados:

            _SalvarTokens(dados)
            _SalvarSessao(dados)

        return CADASTRO_OK

    except Exception as e:

        print(
            "ERRO CadastrarUsuario:",
            e
        )

        return ERRO_CADASTRO


# ============================================================
# LOGIN
# ============================================================
def LoginUsuario(email, senha):
    """
    Retorno:
        0 -> login OK (sessão salva)
        1 -> credenciais inválidas / Supabase recusou o login
        2 -> erro de configuração ou de rede (exceção, sem url/key, etc.)
    """

    url, key = ObterCredenciais()

    if not url or not key:
        return 2

    try:

        r = requests.post(
            f"{url}/auth/v1/token?grant_type=password",
            headers=_headers_auth(key),
            data=json.dumps({
                "email": email,
                "password": senha,
            }),
            timeout=30,
            verify=False,
        )

        if r.status_code != 200:

            print(
                f"ERRO LoginUsuario: "
                f"status {r.status_code} - {r.text}"
            )

            return 1

        dados = r.json()

        # Tokens ficam separados do JSON de sessão.
        _SalvarTokens(dados)

        # Aqui ficam somente nome e e-mail.
        _SalvarSessao(dados)

        return 0

    except Exception as e:

        print(
            "ERRO LoginUsuario:",
            e
        )

        return 2


# ============================================================
# GERENCIAMENTO DOS TOKENS
# ============================================================

def _SalvarTokens(dados):
    """
    Salva somente os tokens em arquivo separado.

    O arquivo recebe permissão 600 quando o sistema suporta
    permissões Unix.
    """

    access_token = dados.get(
        "access_token"
    )

    refresh_token = dados.get(
        "refresh_token"
    )

    if not access_token:
        return

    tokens = {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

    os.makedirs(
        _Pasta_Global,
        exist_ok=True
    )

    with open(
        ARQUIVO_TOKENS,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            tokens,
            f,
            ensure_ascii=False
        )

    # Somente o proprietário pode ler/escrever.
    try:

        os.chmod(
            ARQUIVO_TOKENS,
            0o600
        )

    except Exception:
        pass


def _ObterTokens():
    """
    Retorna os tokens armazenados.

    Retorno:
        dict ou None
    """

    if not os.path.exists(
        ARQUIVO_TOKENS
    ):
        return None

    try:

        with open(
            ARQUIVO_TOKENS,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(
            "ERRO _ObterTokens:",
            e
        )

        return None


def _ObterAccessToken():
    """
    Retorna somente o access_token.
    """

    tokens = _ObterTokens()

    if not tokens:
        return None

    return tokens.get(
        "access_token"
    )


def _ObterRefreshToken():
    """
    Retorna somente o refresh_token.
    """

    tokens = _ObterTokens()

    if not tokens:
        return None

    return tokens.get(
        "refresh_token"
    )


def _LimparTokens():
    """
    Remove completamente os tokens salvos.
    """

    if os.path.exists(
        ARQUIVO_TOKENS
    ):

        try:

            os.remove(
                ARQUIVO_TOKENS
            )

        except Exception as e:

            print(
                "ERRO _LimparTokens:",
                e
            )


# ============================================================
# ATUALIZAR PERFIL
# ============================================================

def AtualizarPerfil(nome=None, telefone=None):

    url, key = ObterCredenciais()
    access_token = _ObterAccessToken()

    if (
        not url
        or not key
        or not access_token
    ):

        print(
            "ERRO AtualizarPerfil: "
            "nenhuma sessão ativa"
        )

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
            headers=_headers_autenticado(
                key,
                access_token
            ),
            data=json.dumps({
                "data": metadata
            }),
            timeout=30,
            verify=False,
        )

        if r.status_code != 200:

            print(
                f"ERRO AtualizarPerfil: "
                f"status {r.status_code} - {r.text}"
            )

            return None

        dados = r.json()

        # Atualiza apenas nome/e-mail no JSON.
        _AtualizarDadosSessao(dados)

        return dados

    except Exception as e:

        print(
            "ERRO AtualizarPerfil:",
            e
        )

        return None


# ============================================================
# ATUALIZAR SENHA
# ============================================================

def AtualizarSenha(nova_senha):

    url, key = ObterCredenciais()
    access_token = _ObterAccessToken()

    if (
        not url
        or not key
        or not access_token
    ):

        print(
            "ERRO AtualizarSenha: "
            "nenhuma sessão ativa"
        )

        return None

    try:

        r = requests.put(
            f"{url}/auth/v1/user",
            headers=_headers_autenticado(
                key,
                access_token
            ),
            data=json.dumps({
                "password": nova_senha
            }),
            timeout=30,
            verify=False,
        )

        if r.status_code != 200:

            print(
                f"ERRO AtualizarSenha: "
                f"status {r.status_code} - {r.text}"
            )

            return None

        dados = r.json()

        _AtualizarDadosSessao(dados)

        # Caso o Supabase forneça novos tokens após
        # alteração da senha, atualizamos os tokens.
        if dados.get("access_token"):

            _SalvarTokens(dados)

        return dados

    except Exception as e:

        print(
            "ERRO AtualizarSenha:",
            e
        )

        return None


# ============================================================
# LOGOUT
# ============================================================

def LogoutUsuario():

    url, key = ObterCredenciais()
    access_token = _ObterAccessToken()

    if (
        url
        and key
        and access_token
    ):

        try:

            requests.post(
                f"{url}/auth/v1/logout",
                headers=_headers_autenticado(
                    key,
                    access_token
                ),
                timeout=30,
                verify=False,
            )

        except Exception as e:

            print(
                "ERRO LogoutUsuario:",
                e
            )

    # Remove os tokens.
    _LimparTokens()

    # Remove nome/e-mail.
    _LimparSessao()


# ============================================================
# VERIFICAR SE ESTÁ LOGADO
# ============================================================

def UsuarioLogado():

    return bool(
        _ObterAccessToken()
    )


# ============================================================
# OBTER SESSÃO
# ============================================================

def ObterSessao():
    """
    Retorna SOMENTE os dados públicos da sessão local.

    Exemplo:

    {
        "nome": "Julio",
        "email": "julio@email.com"
    }
    """

    if not os.path.exists(
        ARQUIVO_SESSAO
    ):
        return None

    try:

        with open(
            ARQUIVO_SESSAO,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(
            "ERRO ObterSessao:",
            e
        )

        return None


# ============================================================
# SALVAR SESSÃO
# ============================================================

def _SalvarSessao(dados):
    """
    Salva SOMENTE nome e e-mail.

    Nenhum token é colocado neste arquivo.
    """

    os.makedirs(
        _Pasta_Global,
        exist_ok=True
    )

    usuario = dados.get(
        "user",
        {}
    )

    metadata = usuario.get(
        "user_metadata",
        {}
    )

    nome = (
        metadata.get("full_name")
        or metadata.get("name")
        or ""
    )

    email = (
        usuario.get("email")
        or dados.get("email")
        or ""
    )

    sessao = {
        "nome": nome,
        "email": email,
    }

    with open(
        ARQUIVO_SESSAO,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            sessao,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# ATUALIZAR DADOS DA SESSÃO
# ============================================================

def _AtualizarDadosSessao(usuario):

    if not usuario:
        return

    metadata = usuario.get(
        "user_metadata",
        {}
    )

    nome = (
        metadata.get("full_name")
        or metadata.get("name")
        or ""
    )

    email = usuario.get(
        "email",
        ""
    )

    sessao = {
        "nome": nome,
        "email": email,
    }

    os.makedirs(
        _Pasta_Global,
        exist_ok=True
    )

    with open(
        ARQUIVO_SESSAO,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            sessao,
            f,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# LIMPAR SESSÃO
# ============================================================

def _LimparSessao():

    if os.path.exists(
        ARQUIVO_SESSAO
    ):

        try:

            os.remove(
                ARQUIVO_SESSAO
            )

        except Exception as e:

            print(
                "ERRO _LimparSessao:",
                e
            )
