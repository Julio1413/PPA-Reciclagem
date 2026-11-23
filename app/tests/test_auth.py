import unittest
from types import SimpleNamespace
from unittest.mock import patch

from Ferramentas import Ferramentas

Ferramentas.DefinirPasta()

from Ferramentas import Auth


class VerificarUsuarioExistenteTests(unittest.TestCase):
    def test_resposta_403_renova_token_antes_de_invalidar_sessao(self):
        tokens = {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
        }
        novos_tokens = {
            "access_token": "novo-access-token",
            "refresh_token": "novo-refresh-token",
        }

        with (
            patch.object(
                Auth,
                "ObterCredenciais",
                return_value=("https://supabase.test", "key"),
            ),
            patch.object(Auth, "_ObterTokens", return_value=tokens),
            patch.object(
                Auth.requests,
                "get",
                side_effect=[
                    SimpleNamespace(status_code=403),
                    SimpleNamespace(status_code=200),
                ],
            ),
            patch.object(
                Auth.requests,
                "post",
                return_value=SimpleNamespace(
                    status_code=200,
                    json=lambda: novos_tokens,
                ),
            ) as refresh_token,
            patch.object(Auth, "_SalvarTokens") as salvar_tokens,
        ):
            self.assertIs(Auth.VerificarUsuarioExistente(), True)
            refresh_token.assert_called_once()
            salvar_tokens.assert_called_once_with(novos_tokens)

    def test_refresh_recusado_invalida_sessao(self):
        tokens = {
            "access_token": "access-token",
            "refresh_token": "refresh-token",
        }

        with (
            patch.object(
                Auth,
                "ObterCredenciais",
                return_value=("https://supabase.test", "key"),
            ),
            patch.object(Auth, "_ObterTokens", return_value=tokens),
            patch.object(
                Auth.requests,
                "get",
                return_value=SimpleNamespace(status_code=403),
            ),
            patch.object(
                Auth.requests,
                "post",
                return_value=SimpleNamespace(status_code=401),
            ),
        ):
            self.assertIs(Auth.VerificarUsuarioExistente(), False)
