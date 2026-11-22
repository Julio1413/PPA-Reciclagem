import flet as ft
from Ferramentas import Supabase, Auth
from Pages import Ui



def MinhaAtividade(page):
    page.views.append(
        ft.View(
            route="/minhaatividade",
            bgcolor=Ui.CorPagina(page),
            controls=[
                Ui.Cabecalho(
                    page=page,
                    destino='/',
                    icone=ft.Icons.STICKY_NOTE_2_ROUNDED,
                    titulo='Minha Atividade'
                )
            ]
        )
    )