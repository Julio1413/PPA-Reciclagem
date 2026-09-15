import flet as ft
from Ferramentas import Ferramentas

def Cabecalho(page):
    pass

def ContainerColor(page):
    """Retorna a cor do container de acordo com o tema de cor do dispositivo"""

    if page.theme_mode == ft.ThemeMode.LIGHT:
        container_color = ft.Colors.WHITE
    else:
        container_color = ft.Colors.BLACK87
    return container_color

def Container(
                page,
                tamanho = None,
                controles=[]
              ):
    """Container para controles"""

    return ft.Container(
        width = page.width,
        height = (tamanho if tamanho else page.height * 0.7),
        bgcolor=ContainerColor(page),
        border_radius=ft.BorderRadius(top_left=32,top_right=32,bottom_left=0,bottom_right=0),
        margin=page.padding*-1,
        padding=10,
        content=ft.ListView(
            controls=controles,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            )
        )

def CorDeFundoSalva():
    arquivo_cor = "CorDeFundo.txt"
    cor_padrao = "GREEN_700"
    if not Ferramentas.ArquivoExiste(arquivo_cor):
        Ferramentas.CriarArquivo(arquivo_cor, cor_padrao)

    cor_pagina = (Ferramentas.LerArquivo(arquivo_cor, cor_padrao) or cor_padrao).strip()
    return getattr(ft.Colors, cor_pagina, ft.Colors.BLACK)