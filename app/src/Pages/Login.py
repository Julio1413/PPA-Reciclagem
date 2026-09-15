import flet as ft
from Ferramentas import Ferramentas
from Pages import Ui

def PaginaLogin(page):
    page.views.append(
        ft.View(
            route='/login',
            bgcolor=Ui.CorDeFundoSalva(),
            controls=[]
        )
    )