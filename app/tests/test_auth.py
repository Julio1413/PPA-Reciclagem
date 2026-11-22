import unittest
from types import SimpleNamespace
from unittest.mock import patch

from Ferramentas import Ferramentas

Ferramentas.DefinirPasta()

from Ferramentas import Auth


class VerificarUsuarioExistenteTests(unittest.TestCase):
    def test_usuario_removido_invalida_sessao(self):
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
            patch.object(Auth.requests, "post") as refresh_token,
        ):
            self.assertIs(Auth.VerificarUsuarioExistente(), False)
            refresh_token.assert_not_called()
