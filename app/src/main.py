import flet as ft
import os
from Ferramentas import Ferramentas, Supabase
from Pages.Ui import NomeDoApp, ObterLocalizacaoCompleta
os.makedirs(Ferramentas.DefinirPasta(), exist_ok=True)
from Ferramentas import Auth


os.system("cls" if os.name == "nt" else "clear")
print('='*20)
print('Aplicação iniciada')

def main(page: ft.Page):
    #Definições da página
    def _AoReceberLocalizacao(dados):
        print("Localização obtida:", dados)

    ObterLocalizacaoCompleta(page, on_result=_AoReceberLocalizacao)
    page.title = NomeDoApp()
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.scroll = ft.ScrollMode.HIDDEN
    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            linux=ft.PageTransitionTheme.CUPERTINO,
            windows=ft.PageTransitionTheme.CUPERTINO,
            android=ft.PageTransitionTheme.CUPERTINO,
            ios=ft.PageTransitionTheme.CUPERTINO,
        )
    )

    
    page.fonts = {
        'Times':'/assets/times.ttf'
    }
    
    page.theme = ft.Theme(
        color_scheme_seed=ft.Colors.GREEN,
        )

    #Sistema de roteamento
    def route(e=None):
        arquivos = ['sessao.json','.sessao_tokens.json']


        if not Ferramentas.ArquivosExistem(arquivos) or not Auth.ObterSessao():
            Ferramentas.DeletarArquivos(arquivos)
            if page.route == '/login1':
                from Pages import Login
                Login.Login(page)

            elif page.route == '/cadastro':
                from Pages import Login
                Login.Cadastro(page)
            else:
                from Pages import Login
                Login.PaginaLogin(page)

        elif page.route == '/':
            from Pages import Home
            page.views.clear()
            Home.Inicio(page)

        elif page.route =='/mapa':
            from Pages import MapView

            async def _AbrirMapa():
                await MapView.Mapa(page)
                page.update()

            page.run_task(_AbrirMapa)
            return

        page.update()

    page.on_route_change = route
    route()



ft.run(main)
