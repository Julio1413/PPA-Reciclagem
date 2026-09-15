import flet as ft
import platform, os
from Ferramentas import Ferramentas

os.makedirs(Ferramentas.DefinirPasta(), exist_ok=True)
from Ferramentas import Auth


def main(page: ft.Page):
    #Definições da página
    page.title = "Reciclagem 622"
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = 'none'
    
    page.fonts = {
        'Times':'/assets/times.ttf'
    }
    
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.GREEN
        )


    #Sistema de roteamento
    def route():
        arquivos = ['sessao.json']
        if not Ferramentas.ArquivosExistem(arquivos) and not Auth.ObterSessao():
            from Pages import Login
            Login.PaginaLogin(page)


        elif page.route=='/':
            page.views.clear()

        
    page.on_route_change = route()



ft.run(main)
