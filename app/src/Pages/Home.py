import platform

import flet as ft
from Pages import Ui, MapUtilities
from Ferramentas import Auth, Supabase, Ferramentas


print('='*20)
print('Tela inicial')

RAIO_PROXIMO_KM = 1
LOCALIDADE_APP = "Valença, BA"


def _FormatarLocalidade(localizacao):
    # IP não identifica com precisão a cidade; no desktop, use a cidade do app.
    if platform.system().lower() not in ("android", "ios", "windows"):
        return LOCALIDADE_APP

    cidade = localizacao.get("cidade")
    estado = localizacao.get("estado")
    if estado and estado.lower() == "bahia":
        estado = "BA"

    if cidade and estado:
        return f"{cidade}, {estado}"
    return cidade or LOCALIDADE_APP


def _CategoriaMaterial(local):
    texto = f'{local.get("Titulo", "")} {local.get("Descrição", "")}'.lower()
    categorias = (
        (("papel", "papelão", "papelao"), "Papel"),
        (("plástico", "plastico", "pet"), "Plástico"),
        (("vidro",), "Vidro"),
        (("metal", "alumínio", "aluminio", "lata"), "Metal"),
        (("eletrônico", "eletronico", "pilha", "bateria"), "Eletrônicos"),
    )
    for termos, categoria in categorias:
        if any(termo in texto for termo in termos):
            return categoria
    return "Materiais diversos"


def Inicio(page):
    texto_localizacao = ft.Text(
        "Obtendo localização...",
        size=14,
        color=Ui.COR_TEXTO_SECUNDARIO,
    )
    coluna_locais = ft.Column(
        expand=True,
        scroll=ft.ScrollMode.AUTO,
        spacing=Ui.ESPACO_MEDIO,
        controls=[],
    )

    def MostrarEstado(icon, titulo, descricao, tentar_novamente=False):
        controles = [
            ft.Icon(icon, size=44, color=Ui.COR_DESTAQUE),
            ft.Text(
                titulo,
                size=17,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Text(
                descricao,
                size=14,
                color=Ui.COR_TEXTO_SECUNDARIO,
                text_align=ft.TextAlign.CENTER,
            ),
        ]
        if tentar_novamente:
            controles.append(
                ft.Button(
                    on_click=lambda _: page.run_task(ObterLocalizacao),
                    bgcolor=ft.Colors.TRANSPARENT,
                    content=ft.Text(
                        "Tentar novamente",
                        color=Ui.COR_DESTAQUE,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            )
        coluna_locais.controls = [
            ft.Container(
                expand=True,
                padding=Ui.ESPACO_GRANDE,
                border_radius=Ui.RAIO_CARTAO,
                bgcolor=Ui.COR_SUPERFICIE_ELEVADA,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=Ui.ESPACO_PEQUENO,
                    controls=controles,
                ),
            )
        ]
        page.update()

    def CriarCartaoLocal(local, distancia):
        descricao = local.get("Descrição") or "Sem descrição disponível."
        titulo = local.get("Titulo") or "Ponto de coleta"

        return ft.Container(
            ink=True,
            on_click=lambda e, km=distancia: Ui.Sheet(
                e, page, distancia=km
            ),
            data=local,
            padding=Ui.ESPACO_MEDIO,
            border_radius=Ui.RAIO_CARTAO,
            border=ft.Border.all(1, Ui.COR_CONTORNO),
            bgcolor=Ui.COR_SUPERFICIE_ELEVADA,
            content=ft.Column(
                spacing=Ui.ESPACO_PEQUENO,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                expand=True,
                                spacing=Ui.ESPACO_PEQUENO,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.RECYCLING_ROUNDED,
                                        color=Ui.COR_DESTAQUE,
                                        size=24,
                                    ),
                                    ft.Column(
                                        expand=True,
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                _CategoriaMaterial(local),
                                                size=12,
                                                color=Ui.COR_DESTAQUE,
                                            ),
                                            ft.Text(
                                                titulo,
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            ft.Container(
                                bgcolor=Ui.COR_DESTAQUE,
                                border_radius=20,
                                padding=ft.Padding.only(
                                    left=Ui.ESPACO_PEQUENO,
                                    right=Ui.ESPACO_PEQUENO,
                                    top=8,
                                    bottom=8,
                                ),
                                content=ft.Text(
                                    f"{distancia:.2f} km",
                                    size=13,
                                    weight=ft.FontWeight.BOLD,
                                    color=Ui.COR_SUPERFICIE_ESCURA,
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Text(
                                descricao,
                                size=13,
                                color=Ui.COR_TEXTO_SECUNDARIO,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                expand=True,
                            ),
                            ft.Icon(
                                ft.Icons.ARROW_FORWARD_ROUNDED,
                                color=Ui.COR_TEXTO_SECUNDARIO,
                                size=20,
                            ),
                        ],
                    ),
                ],
            ),
        )

    async def ObterLocalizacao():
        coluna_locais.controls = [
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=Ui.ESPACO_MEDIO,
                    controls=[
                        ft.ProgressRing(color=Ui.COR_DESTAQUE),
                        ft.Text(
                            "Buscando pontos próximos...",
                            color=Ui.COR_TEXTO_SECUNDARIO,
                        ),
                    ],
                ),
            )
        ]
        page.update()

        try:
            localizacao = await MapUtilities.ObterLocalizacao(page)
            texto_localizacao.value = _FormatarLocalidade(localizacao)

            locais = Supabase.LerTabela(
                "PontosColeta",
                {"Reservado": "eq.False"},
            )
            pontos_proximos = []
            for local in locais:
                distancia = Ferramentas.CalcularDistancia(
                    (
                        float(local["Latitude"]),
                        float(local["Longitude"]),
                    ),
                    (
                        float(localizacao["latitude"]),
                        float(localizacao["longitude"]),
                    ),
                )
                if distancia <= RAIO_PROXIMO_KM:
                    pontos_proximos.append((distancia, local))

            pontos_proximos.sort(key=lambda ponto: ponto[0])
            coluna_locais.controls.clear()
            if pontos_proximos:
                coluna_locais.controls.extend(
                    CriarCartaoLocal(local, distancia)
                    for distancia, local in pontos_proximos
                )
            else:
                MostrarEstado(
                    ft.Icons.LOCATION_SEARCHING_ROUNDED,
                    "Nenhum ponto próximo",
                    "Ainda não há pontos de coleta em um raio de 1 km.",
                )
                return
            page.update()
        except Exception as erro:
            print(f"Erro ao carregar pontos próximos: {erro}")
            texto_localizacao.value = LOCALIDADE_APP
            MostrarEstado(
                ft.Icons.ERROR_OUTLINE_ROUNDED,
                "Não foi possível carregar os pontos",
                "Verifique sua conexão e a permissão de localização.",
                tentar_novamente=True,
            )

    sessao = Auth.ObterSessao()
    nome = sessao.get("nome", "pessoa").strip().split()[0]

    def CartaoAcao(titulo, descricao, icone, rota):
        return ft.Container(
            expand=True,
            height=112,
            ink=True,
            on_click=lambda _: Ui.IrPara(rota, page),
            padding=Ui.ESPACO_MEDIO,
            border_radius=Ui.RAIO_CARTAO,
            bgcolor=Ui.COR_SUPERFICIE_ELEVADA,
            border=ft.Border.all(1, Ui.COR_CONTORNO),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.Icon(icone, size=26, color=Ui.COR_DESTAQUE),
                            ft.Icon(
                                ft.Icons.ARROW_FORWARD_ROUNDED,
                                size=18,
                                color=Ui.COR_TEXTO_SECUNDARIO,
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                titulo,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE,
                            ),
                            ft.Text(
                                descricao,
                                size=11,
                                color=Ui.COR_TEXTO_SECUNDARIO,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ],
            ),
        )

    page.views.append(
        ft.View(
            bgcolor=Ui.CorPagina(page),
            route="/",
            controls=[
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        Ui.Cabecalho(
                            page=page,
                            titulo=Ui.NomeDoApp(),
                            destino="/",
                            icone_btn=ft.Icons.LOGIN_ROUNDED,
                            fundo=Ui.CorDeFundoSalva(),
                        ),
                        ft.Container(
                            expand=True,
                            padding=Ui.ESPACO_MEDIO,
                            content=ft.Column(
                                expand=True,
                                spacing=Ui.ESPACO_MEDIO,
                                controls=[
                                    ft.Column(
                                        spacing=Ui.ESPACO_PEQUENO,
                                        controls=[
                                            ft.Text(
                                                f"Olá, {nome}",
                                                size=23,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE,
                                            ),
                                            ft.Row(
                                                spacing=Ui.ESPACO_PEQUENO,
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.PIN_DROP_OUTLINED,
                                                        color=Ui.COR_DESTAQUE,
                                                        size=20,
                                                    ),
                                                    texto_localizacao,
                                                ],
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        spacing=Ui.ESPACO_MEDIO,
                                        controls=[
                                            CartaoAcao(
                                                "Abrir mapa",
                                                "Encontre pontos de coleta",
                                                ft.Icons.MAP_ROUNDED,
                                                "/mapa",
                                            ),
                                            CartaoAcao(
                                                "Minha atividade",
                                                "Acompanhe suas ações",
                                                ft.Icons.STICKY_NOTE_2_ROUNDED,
                                                "/minhaatividade",
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        vertical_alignment=ft.CrossAxisAlignment.END,
                                        controls=[
                                            ft.Text(
                                                "Pontos próximos",
                                                size=18,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE,
                                            ),
                                            ft.Text(
                                                "Raio de 1 km",
                                                size=12,
                                                color=Ui.COR_TEXTO_SECUNDARIO,
                                            ),
                                        ],
                                    ),
                                    coluna_locais,
                                ],
                            ),
                        ),
                    ],
                )
            ],
        )
    )
    page.update()
    page.run_task(ObterLocalizacao)
