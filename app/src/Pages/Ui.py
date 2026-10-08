import asyncio

import requests
import flet as ft
import flet_geolocator as ftg
from Ferramentas import Ferramentas

print('='*20)
print('Módulo Ui')

_PERMISSOES_LOCALIZACAO_OK = (
    getattr(ftg.GeolocatorPermissionStatus, "WHILE_IN_USE", "while_in_use"),
    getattr(ftg.GeolocatorPermissionStatus, "ALWAYS", "always"),
)


def _StatusPermissaoNormalizado(status):
    """Normaliza um status de permissão para comparação entre enums e valores simulados em testes."""
    if status is None:
        return None
    if hasattr(status, "value"):
        status = status.value
    if hasattr(status, "name"):
        status = status.name
    if isinstance(status, str):
        return status.strip().replace(" ", "_").lower()
    return str(status).strip().replace(" ", "_").lower()


def _PermissaoConcedida(status):
    """Indica se a permissão de localização já foi aprovada."""
    valor = _StatusPermissaoNormalizado(status)
    return valor in {"while_in_use", "always"}


def _PermissaoPermanente(status):
    """Indica se a permissão foi negada permanentemente."""
    valor = _StatusPermissaoNormalizado(status)
    return valor in {"denied_forever", "permanently_denied"}


def _PermissaoNegada(status):
    """Indica se a permissão foi negada de forma definitiva ou temporária."""
    valor = _StatusPermissaoNormalizado(status)
    return valor in {"denied", "denied_forever", "permanently_denied"}


def _ServicoLocalizacao(page):
    """Retorna o Geolocator registrado na página, criando-o se necessário."""
    if not hasattr(page, "services"):
        page.services = []

    for servico in page.services:
        if isinstance(servico, ftg.Geolocator):
            return servico

    geo = ftg.Geolocator()
    page.services.append(geo)
    return geo


def _CidadePorEndereco(endereco):
    """Extrai a cidade do payload de endereço do Nominatim."""
    if not isinstance(endereco, dict):
        return None

    for campo in ("city", "town", "village", "municipality"):
        valor = endereco.get(campo)
        if valor:
            return valor
    return None


def _EstadoPorEndereco(endereco):
    """Extrai o estado do payload de endereço do Nominatim."""
    if not isinstance(endereco, dict):
        return None

    for campo in ("state", "province", "region"):
        valor = endereco.get(campo)
        if valor:
            return valor
    return None


def NomeDoApp():
    return 'ReciclaJá Valença'

def IrPara(rota, page):
    """Navega imediatamente para a rota desejada e força a execução do handler da rota no mesmo clique."""
    page.route = rota
    if callable(getattr(page, "on_route_change", None)):
        page.on_route_change(None)
    else:
        page.navigate(rota)
    page.update()

def Cabecalho(
            titulo,
            page,
            destino="/",                   
            icone=ft.Icons.RECYCLING_ROUNDED,
            icone_btn=ft.Icons.ARROW_BACK_IOS_ROUNDED,
            ):
    return ft.Column(controls=[ft.Container(height=90,margin=-10,
        content=ft.Container(alignment=ft.Alignment.BOTTOM_CENTER,
            padding=ft.Padding.only(left=10, right=10, bottom=10),
            blur=(10, 10),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon_color=ft.Colors.WHITE,
                        icon=icone_btn,
                        on_click=lambda _: IrPara(destino, page),   # usa o mesmo caminho robusto do IrPara
                        icon_size=25,
                    ),
                    ft.Text(value=titulo, color=ft.Colors.WHITE, size=20, weight=ft.FontWeight.BOLD),
                    ft.Icon(icon=icone, color=ft.Colors.WHITE, size=30),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            height=50,
        ),
    ),
    ft.Placeholder(color=ft.Colors.TRANSPARENT, height=5)
                               ])

def ContainerColor(page):
    """Retorna a cor do container de acordo com o tema de cor do dispositivo"""

    if page.theme_mode == ft.ThemeMode.LIGHT:
        container_color = ft.Colors.WHITE
    else:
        container_color = ft.Colors.BLACK_87
    return container_color

def Container(
                page,
                tamanho = None,
                controles=[],
                scroll=ft.ScrollMode.AUTO
              ):
    """Container para controles"""

    return ft.Column(
        expand=True,
        alignment=ft.MainAxisAlignment.END,
        controls=[
            ft.Container(
                width = page.width,
                height = (tamanho if tamanho else page.height * 0.8),
                bgcolor=ContainerColor(page),
                border_radius=ft.BorderRadius(top_left=22,top_right=22,bottom_left=0,bottom_right=0),
                margin=-10,
                padding=10,
                content=ft.Column(
                    spacing=10,
                    scroll=scroll,
                    controls=controles
                    )
                )
            ]
        )

def CorDeFundoSalva():
    arquivo_cor = "CorDeFundo.txt"
    cor_padrao = "GREEN_800"
    if not Ferramentas.ArquivoExiste(arquivo_cor):
        Ferramentas.CriarArquivo(arquivo_cor, cor_padrao)

    cor_pagina = (Ferramentas.LerArquivo(arquivo_cor, cor_padrao) or cor_padrao).strip()
    return getattr(ft.Colors, cor_pagina, ft.Colors.BLACK)


def ObterLocalizacaoCompleta(page, on_result=None):
    """Solicita a localização atual do dispositivo e retorna coordenadas, cidade e estado via callback.

    A função mantém a assinatura síncrona usada no projeto. Internamente, ela agenda uma
    coroutine na fila do Flet com `page.run_task(...)` e entrega o resultado em `on_result`.

    Fluxo de resolução:
      1. tenta obter permissão e GPS do dispositivo;
      2. geocodifica reversamente para cidade/estado;
      3. se a localização via GPS ou geocodificação falharem, tenta obter os dados por IP;
      4. se tudo falhar, retorna um dicionário com erro explícito.

    Formato do payload em caso de sucesso:
        {
            "latitude": float,
            "longitude": float,
            "cidade": str | None,
            "estado": str | None,
        }

    Em caso de falha de permissão, o callback recebe:
        {"erro": "permissao_negada"}

    Em caso de falha de geocodificação reversa, o callback recebe:
        {
            "latitude": float,
            "longitude": float,
            "cidade": None,
            "estado": None,
            "erro": "geocodificacao_falhou",
        }
    """
    geo = _ServicoLocalizacao(page)

    async def _TentarIp(latitude=None, longitude=None):
        """Tenta obter latitude, longitude, cidade e estado por IP como fallback."""
        try:
            resposta = await asyncio.to_thread(
                lambda: requests.get(
                    "https://ipinfo.io/json",
                    timeout=5,
                )
            )
            resposta.raise_for_status()
            dados = resposta.json()
            if not isinstance(dados, dict):
                return None

            loc = dados.get("loc")
            if isinstance(loc, str) and "," in loc:
                partes = [parte.strip() for parte in loc.split(",", 1)]
                if len(partes) == 2:
                    latitude = float(partes[0])
                    longitude = float(partes[1])

            cidade = dados.get("city")
            estado = dados.get("region")

            return {
                "latitude": latitude,
                "longitude": longitude,
                "cidade": cidade,
                "estado": estado,
            }
        except Exception:
            return None

    async def _FluxoLocalizacaoCompleta():
        try:
            status = await geo.get_permission_status()
        except Exception:
            status = None

        if _PermissaoPermanente(status):
            fallback_ip = await _TentarIp()
            if fallback_ip:
                if on_result:
                    on_result(fallback_ip)
                return
            if on_result:
                on_result({"erro": "permissao_negada"})
            return

        if not _PermissaoConcedida(status):
            try:
                status = await geo.request_permission()
            except Exception:
                status = None

            if _PermissaoPermanente(status) or not _PermissaoConcedida(status):
                fallback_ip = await _TentarIp()
                if fallback_ip:
                    if on_result:
                        on_result(fallback_ip)
                    return
                if on_result:
                    on_result({"erro": "permissao_negada"})
                return

        latitude = None
        longitude = None

        try:
            posicao = await geo.get_current_position(
                accuracy=ftg.GeolocatorPositionAccuracy.BEST
            )
            latitude = float(posicao.latitude)
            longitude = float(posicao.longitude)
        except Exception:
            latitude = None
            longitude = None

        resultado = {
            "latitude": latitude,
            "longitude": longitude,
            "cidade": None,
            "estado": None,
        }

        if latitude is None or longitude is None:
            fallback_ip = await _TentarIp(latitude, longitude)
            if fallback_ip:
                if on_result:
                    on_result(fallback_ip)
                return
            if on_result:
                on_result({"erro": "localizacao_indisponivel"})
            return

        try:
            resposta = await asyncio.to_thread(
                lambda: requests.get(
                    "https://nominatim.openstreetmap.org/reverse",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "format": "jsonv2",
                        "accept-language": "pt-BR",
                    },
                    headers={"User-Agent": "ReciclaJa-Valenca/1.0"},
                    timeout=5,
                )
            )
            resposta.raise_for_status()

            dados = resposta.json()
            endereco = dados.get("address", {}) if isinstance(dados, dict) else {}
            resultado["cidade"] = _CidadePorEndereco(endereco)
            resultado["estado"] = _EstadoPorEndereco(endereco)
        except Exception:
            fallback_ip = await _TentarIp(latitude, longitude)
            if fallback_ip:
                if on_result:
                    on_result(fallback_ip)
                return

            resultado["cidade"] = None
            resultado["estado"] = None
            resultado["erro"] = "geocodificacao_falhou"
            if on_result:
                on_result(resultado)
            return

        if on_result:
            on_result(resultado)

    page.run_task(_FluxoLocalizacaoCompleta)