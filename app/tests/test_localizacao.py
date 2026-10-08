import asyncio
from types import SimpleNamespace

import pytest

from Pages import Ui


class FakePage:
    def __init__(self):
        self.services = []

    def run_task(self, coro):
        return asyncio.create_task(coro())


class FakeGeolocator:
    def __init__(self, permission_status="while_in_use", position=None, request_status=None):
        self.permission_status = permission_status
        self.request_status = request_status
        self.request_calls = 0
        self.current_position = position or SimpleNamespace(latitude=-12.9, longitude=-38.4)

    async def get_permission_status(self):
        return self.permission_status

    async def request_permission(self):
        self.request_calls += 1
        if self.request_status is not None:
            self.permission_status = self.request_status
        return self.permission_status

    async def get_current_position(self, accuracy=None):
        return self.current_position


class FakeResponse:
    def __init__(self, payload=None, exc=None):
        self.payload = payload or {}
        self.exc = exc

    def raise_for_status(self):
        if self.exc is not None:
            raise self.exc

    def json(self):
        return self.payload


@pytest.fixture
def fake_ftg(monkeypatch):
    status = SimpleNamespace(
        WHILE_IN_USE="while_in_use",
        ALWAYS="always",
        PERMANENTLY_DENIED="permanently_denied",
        DENIED="denied",
    )
    accuracy = SimpleNamespace(BEST="best")

    def fabrica(permission_status="while_in_use", position=None, request_status=None):
        return FakeGeolocator(
            permission_status=permission_status,
            position=position,
            request_status=request_status,
        )

    monkeypatch.setattr(Ui.ftg, "GeolocatorPermissionStatus", status)
    monkeypatch.setattr(Ui.ftg, "GeolocatorPositionAccuracy", accuracy)
    monkeypatch.setattr(Ui.ftg, "Geolocator", fabrica)
    return status


async def _AguardarCallback(resultado, timeout=1.0):
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        if resultado.get("valor") is not None:
            return resultado["valor"]
        await asyncio.sleep(0.01)
    raise AssertionError("Callback não foi invocado")


@pytest.mark.asyncio
async def test_permissao_ja_concedida_nao_pede_novamente(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(permission_status="while_in_use")
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)
    monkeypatch.setattr(Ui.requests, "get", lambda *args, **kwargs: FakeResponse({"address": {"city": "Valença", "state": "Bahia"}}))

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert geolocator.request_calls == 0
    assert resultado["valor"]["cidade"] == "Valença"
    assert resultado["valor"]["estado"] == "Bahia"


@pytest.mark.asyncio
async def test_permissao_negada_antes_de_conceder_deve_pedir_e_sucessar(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(permission_status="denied", request_status="while_in_use")
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)
    monkeypatch.setattr(Ui.requests, "get", lambda *args, **kwargs: FakeResponse({"address": {"city": "Salvador", "state": "Bahia"}}))

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert geolocator.request_calls == 1
    assert resultado["valor"]["cidade"] == "Salvador"
    assert resultado["valor"]["estado"] == "Bahia"


@pytest.mark.asyncio
async def test_permissao_negada_apos_solicitacao_tenta_fallback_ip(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(permission_status="denied", request_status="denied")
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)
    monkeypatch.setattr(
        Ui.requests,
        "get",
        lambda *args, **kwargs: FakeResponse({"loc": "-12.97,-38.51", "city": "Salvador", "region": "Bahia"}),
    )

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert resultado["valor"]["latitude"] == -12.97
    assert resultado["valor"]["longitude"] == -38.51
    assert resultado["valor"]["cidade"] == "Salvador"
    assert resultado["valor"]["estado"] == "Bahia"


@pytest.mark.asyncio
async def test_permissao_permanente_negada_nao_pede_novamente_e_tenta_ip(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(permission_status="permanently_denied")
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)
    monkeypatch.setattr(
        Ui.requests,
        "get",
        lambda *args, **kwargs: FakeResponse({"loc": "-13.0,-38.5", "city": "Salvador", "region": "Bahia"}),
    )

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert geolocator.request_calls == 0
    assert resultado["valor"]["cidade"] == "Salvador"
    assert resultado["valor"]["estado"] == "Bahia"


@pytest.mark.asyncio
async def test_geocodificacao_timeout_preserva_coordenadas(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(position=SimpleNamespace(latitude=-12.5, longitude=-38.1))
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)

    def erro_get(*args, **kwargs):
        raise TimeoutError("timeout")

    monkeypatch.setattr(Ui.requests, "get", erro_get)

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert resultado["valor"]["latitude"] == -12.5
    assert resultado["valor"]["longitude"] == -38.1
    assert resultado["valor"]["cidade"] is None
    assert resultado["valor"]["estado"] is None
    assert resultado["valor"]["erro"] == "geocodificacao_falhou"


@pytest.mark.asyncio
async def test_api_sem_city_usa_fallbacks_e_estado(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(position=SimpleNamespace(latitude=-1.0, longitude=-2.0))
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)
    monkeypatch.setattr(
        Ui.requests,
        "get",
        lambda *args, **kwargs: FakeResponse({"address": {"municipality": "Feira de Santana", "state": "Bahia"}}),
    )

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert resultado["valor"]["cidade"] == "Feira de Santana"
    assert resultado["valor"]["estado"] == "Bahia"
    assert "erro" not in resultado["valor"]


@pytest.mark.asyncio
async def test_api_sem_state_envia_estado_none(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(position=SimpleNamespace(latitude=-3.0, longitude=-4.0))
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)
    monkeypatch.setattr(
        Ui.requests,
        "get",
        lambda *args, **kwargs: FakeResponse({"address": {"city": "Aracaju"}}),
    )

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert resultado["valor"]["cidade"] == "Aracaju"
    assert resultado["valor"]["estado"] is None


@pytest.mark.asyncio
async def test_multiplas_chamadas_nao_duplicam_servico(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(position=SimpleNamespace(latitude=-10.0, longitude=-20.0))
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)
    monkeypatch.setattr(Ui.requests, "get", lambda *args, **kwargs: FakeResponse({"address": {"city": "Itabuna", "state": "Bahia"}}))

    resultados = []
    for _ in range(2):
        Ui.ObterLocalizacaoCompleta(page, lambda payload, idx=len(resultados): resultados.append(payload))
    await asyncio.sleep(0.05)

    assert len(page.services) == 1
    assert len(resultados) == 2
    assert all(item["cidade"] == "Itabuna" for item in resultados)


@pytest.mark.asyncio
async def test_localizacao_indisponivel_sem_gps_fisico_tenta_ip(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(position=SimpleNamespace(latitude=-44.0, longitude=-60.0))
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)

    async def get_current_position(*args, **kwargs):
        raise RuntimeError("GPS indisponível")

    geolocator.get_current_position = get_current_position

    def resposta_por_url(url, *args, **kwargs):
        if "nominatim" in str(url):
            raise TimeoutError("timeout")
        return FakeResponse({"loc": "-13.0100,-38.5100", "city": "Salvador", "region": "Bahia"})

    monkeypatch.setattr(Ui.requests, "get", resposta_por_url)

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert resultado["valor"]["latitude"] == -13.01
    assert resultado["valor"]["longitude"] == -38.51
    assert resultado["valor"]["cidade"] == "Salvador"
    assert resultado["valor"]["estado"] == "Bahia"


@pytest.mark.asyncio
async def test_fallback_por_ip_quando_gps_ou_geocodificacao_falham(monkeypatch, fake_ftg):
    page = FakePage()
    geolocator = FakeGeolocator(position=SimpleNamespace(latitude=-44.0, longitude=-60.0))
    page.services.append(geolocator)
    monkeypatch.setattr(Ui, "_ServicoLocalizacao", lambda p: geolocator)

    async def get_current_position(*args, **kwargs):
        raise RuntimeError("GPS indisponível")

    geolocator.get_current_position = get_current_position

    def resposta_por_endereco(*args, **kwargs):
        raise TimeoutError("timeout")

    def resposta_por_ip(*args, **kwargs):
        if args and getattr(args[0], "startswith", lambda _: False)("https://nominatim"):
            raise TimeoutError("timeout")
        return FakeResponse({"loc": "-13.0100,-38.5100", "city": "Salvador", "region": "Bahia"})

    monkeypatch.setattr(Ui.requests, "get", resposta_por_ip)

    resultado = {"valor": None}
    Ui.ObterLocalizacaoCompleta(page, lambda payload: resultado.__setitem__("valor", payload))
    await asyncio.sleep(0.05)

    assert resultado["valor"]["latitude"] == -13.01
    assert resultado["valor"]["longitude"] == -38.51
    assert resultado["valor"]["cidade"] == "Salvador"
    assert resultado["valor"]["estado"] == "Bahia"
