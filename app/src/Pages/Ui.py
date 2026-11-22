import asyncio
from urllib.parse import quote
import requests
import flet as ft
import flet_geolocator as ftg
from Ferramentas import Ferramentas, Auth, Supabase
from Pages import MapView

print('='*20)
print('Módulo Ui')

ESPACO_PEQUENO = 8
ESPACO_MEDIO = 16
ESPACO_GRANDE = 24
RAIO_CARTAO = 16
COR_PRIMARIA = ft.Colors.GREEN_800
COR_SUPERFICIE_ESCURA = "#151B17"
COR_SUPERFICIE_ELEVADA = "#222B25"
COR_TEXTO_SECUNDARIO = "#C2CCC5"
COR_DESTAQUE = "#B7E4C7"
COR_CONTORNO = "#59645C"


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


def _TemaEscuro(page):
    return page.theme_mode == ft.ThemeMode.DARK or (
        page.theme_mode == ft.ThemeMode.SYSTEM
        and page.platform_brightness == ft.Brightness.DARK
    )


def Sheet(e,page,distancia=None, pode_reservar=True):
    local = e.control.data
    texto_distancia = ft.Text(
        f'Distância: {distancia:.2f} km'
        if distancia is not None
        else 'Calculando distância...',
        size=14,
        weight=ft.FontWeight.BOLD,
        color=COR_DESTAQUE,
    )

    async def ObterLocalizacao():
        from Pages import MapUtilities
        nonlocal distancia
        try:
            loc = await MapUtilities.ObterLocalizacao(page)
            distancia = Ferramentas.CalcularDistancia(
                (float(local['Latitude']), float(local['Longitude'])),
                (float(loc['latitude']), float(loc['longitude']))
            )
            texto_distancia.value = f'Distância: {distancia:.2f} km'
            page.update()
        except Exception:
            texto_distancia.value = 'Distância indisponível'
            page.update()
            raise

    def Fechar():
        sheet.open = False
        page.update()
    
    destinatario = local['EmailCriador']
    assunto = quote("Solicitação de mais informações.")
    sessao = Auth.ObterSessao()
    mensagem = quote(
        f'Olá! Sou {sessao["nome"]} e reservei os materiais de '
        f'"{local["Titulo"]}". Poderia me dar mais informações para a coleta?'
    )

    link = f"mailto:{destinatario}?subject={assunto}&body={mensagem}"
    

    def ReservarEMandarEmail():
        if Supabase.AtualizarLinha(
            nome_tabela='PontosColeta',
            filtros={'id': f"eq.{local['id']}"},
            novos_dados={'Reservado': 'True', 'ReservadoPor': Auth.ObterSessao()['email']},
        ):
            pass
        Fechar()


    sheet = ft.CupertinoBottomSheet(
        content=ft.Column(
            height=page.height * 0.5,
            spacing=ESPACO_MEDIO,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Row(
                    width=page.width,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            height=4,
                            width=40,
                            bgcolor=COR_TEXTO_SECUNDARIO,
                            border_radius=4,
                            margin=ESPACO_PEQUENO,
                        )
                    ]
                ),
                ft.Container(
                    bgcolor=COR_SUPERFICIE_ELEVADA,
                    border_radius=RAIO_CARTAO,
                    padding=ESPACO_GRANDE,
                    margin=ft.Margin.only(left=ESPACO_MEDIO, right=ESPACO_MEDIO),
                    content=ft.Column(
                        spacing=ESPACO_MEDIO,
                        controls=[
                            ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=ft.CrossAxisAlignment.START,
                                controls=[
                                    ft.Text(
                                        local["Titulo"],
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        expand=True,
                                    ),
                                    ft.Icon(
                                        ft.Icons.LOCATION_ON_ROUNDED,
                                        color=COR_DESTAQUE,
                                        size=28,
                                    ),
                                ],
                            ),
                            ft.Container(
                                bgcolor=COR_SUPERFICIE_ESCURA,
                                border_radius=RAIO_CARTAO,
                                padding=ESPACO_MEDIO,
                                content=ft.Row(
                                    spacing=ESPACO_PEQUENO,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.NEAR_ME_ROUNDED,
                                            color=COR_DESTAQUE,
                                            size=20,
                                        ),
                                        texto_distancia,
                                    ],
                                ),
                            ),
                            ft.Column(
                                spacing=ESPACO_PEQUENO,
                                controls=[
                                    ft.Text(
                                        "Sobre este ponto",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        local["Descrição"],
                                        size=15,
                                        color=COR_TEXTO_SECUNDARIO,
                                        selectable=True,
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=ESPACO_PEQUENO,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.PERSON_OUTLINE_ROUNDED,
                                        color=COR_TEXTO_SECUNDARIO,
                                        size=20,
                                    ),
                                    ft.Text(
                                        f'Publicado por {local["NomeCriador"]}',
                                        size=14,
                                        color=COR_TEXTO_SECUNDARIO,
                                    ),
                                ],
                            ),
                            ft.Text(
                                " · ".join(
                                    (
                                        f'Lat. {MapView._FormatarCoordenada(local["Latitude"])}',
                                        f'Lon. {MapView._FormatarCoordenada(local["Longitude"])}',
                                        f'ID {local["id"]}',
                                    )
                                ),
                                size=11,
                                color=COR_TEXTO_SECUNDARIO,
                                selectable=True,
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    action=ft.OpenUrl(link, target=ft.UrlTarget.BLANK),
                    on_click=lambda e: ReservarEMandarEmail() if pode_reservar else None,
                    ink=True,
                    bgcolor=CorDeFundoSalva(),
                    border_radius=RAIO_CARTAO,
                    height=56,
                    margin=ft.Margin.only(left=ESPACO_MEDIO, right=ESPACO_MEDIO),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=ESPACO_PEQUENO,
                        controls=[
                            ft.Icon(ft.Icons.EMAIL_ROUNDED, color=ft.Colors.WHITE),
                            ft.Text(
                                'Reservar e mandar e-mail',
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                        ],
                    ),
                ),
                ft.Container(
                    on_click=lambda _: Fechar(),
                    ink=True,
                    border=ft.Border.all(1, COR_CONTORNO),
                    border_radius=RAIO_CARTAO,
                    height=56,
                    margin=ft.Margin.only(
                        left=ESPACO_MEDIO,
                        right=ESPACO_MEDIO,
                        bottom=ESPACO_GRANDE,
                    ),
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=ESPACO_PEQUENO,
                        controls=[
                            ft.Icon(ft.Icons.CLOSE_ROUNDED, color=COR_TEXTO_SECUNDARIO),
                            ft.Text(
                                'Cancelar',
                                size=15,
                                color=COR_TEXTO_SECUNDARIO,
                            ),
                        ],
                    ),
                ),
            ]
        )
    )
    
    page.overlay.append(sheet)
    sheet.open = True
    if distancia is None:
        page.run_task(ObterLocalizacao)



def Cabecalho(
            titulo,
            page,
            destino="/",                   
            icone=ft.Icons.RECYCLING_ROUNDED,
            icone_btn=ft.Icons.ARROW_BACK_IOS_ROUNDED,
            fundo=None,
            ):
    return ft.Column(
        controls=[
            
            ft.Placeholder(color=ft.Colors.TRANSPARENT, height=5),
            ft.Container(
                bgcolor=fundo if fundo else CorDeFundoSalva(),
                padding=10,
                border_radius=16,
                content=ft.Row(
                    controls=[
                        ft.IconButton(
                            icon_color=ft.Colors.WHITE,
                            icon=icone_btn,
                            on_click=lambda _: IrPara(destino, page),
                            icon_size=25,
                        ),
                        ft.Text(
                            value=titulo,
                            color=ft.Colors.WHITE,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Icon(icon=icone, color=ft.Colors.WHITE, size=30),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
            ),
        ]
    )



def CorPagina (page):
    if _TemaEscuro(page):
        container_color = ft.Colors.BLACK_87
    else:
        container_color = ft.Colors.WHITE
    return 


def TextColor(page,opacidade:float|int=1):
    """Retorna a cor do container de acordo com o tema de cor do dispositivo"""

    if _TemaEscuro(page):
        container_color = ft.Colors.WHITE
    else:
        container_color = ft.Colors.BLACK_87
    return ft.Colors.with_opacity(opacidade, container_color)


def ContainerColor(page,opacidade:float|int=1):
    """Retorna a cor do container de acordo com o tema de cor do dispositivo"""

    if not _TemaEscuro(page):
        container_color = ft.Colors.WHITE
    else:
        container_color = COR_SUPERFICIE_ELEVADA
    return ft.Colors.with_opacity(opacidade, container_color)

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