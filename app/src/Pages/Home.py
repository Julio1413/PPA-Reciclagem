import asyncio
import flet as ft
import requests
from Pages import Ui, MapUtilities
from Ferramentas import Auth

print('='*20)
print('Tela inicial')

def ObtercidadeIp():
    resposta = requests.get("http://ip-api.com/json/", timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()
 
    if dados.get("status") != "success":
        return None
 
    return dados
 

def Inicio (page):

    texto_localizacao = ft.Text('Obtendo localização...', size=15, color=ft.Colors.WHITE)

    async def _CarregarCidadeIp():
        # requests.get é bloqueante -> roda em thread separada para não
        # travar o event loop (e, com ele, os cliques na página)
        cidade_ip = await asyncio.to_thread(ObtercidadeIp)
        texto_localizacao.value = (
            f'{cidade_ip["city"]}, {cidade_ip["region"]}' if cidade_ip else 'Localização indisponível'
        )
        page.update()

    page.run_task(_CarregarCidadeIp)

    page.views.append(
            ft.View(
                bgcolor=Ui.CorDeFundoSalva(),
                route='/',
                controls=[
                    Ui.Cabecalho(
                        page=page,
                        titulo=Ui.NomeDoApp(),
                        destino='/',
                        icone_btn=ft.Icons.LOGIN_ROUNDED,
                    ),
                    ft.Column(
                        spacing=3,
                        controls=[
                            ft.Text(f'Olá, {Auth.ObterSessao()['nome']}',size=17,color=ft.Colors.WHITE),
                            ft.Row(
                                spacing=1,
                                alignment=ft.MainAxisAlignment.START,
                                controls=[
                                    ft.Icon(icon=ft.Icons.PIN_DROP_OUTLINED,color=ft.Colors.WHITE,size=20),
                                    texto_localizacao,
                                ]
                            ),
                            
                        ]
                    ),
                    ft.Placeholder(color=ft.Colors.TRANSPARENT, height=2),
                    Ui.Container(
                        tamanho=page.height*0.85,
                        page=page,
                        controles=[
                            ft.Button(
                                on_click=lambda _:Ui.IrPara('/mapa',page),
                                style=ft.ButtonStyle(padding=-10),
                                height=70,
                                bgcolor=ft.Colors.TRANSPARENT,
                                content=ft.Container(
                                    height=60,
                                    padding=10,
                                    border_radius=12,
                                    bgcolor=Ui.CorDeFundoSalva(),
                                    content=ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Icon(icon=ft.Icons.MAP_ROUNDED, color=ft.Colors.WHITE,size=30),
                                            ft.Text('Abrir mapa',color=ft.Colors.WHITE,size=20,weight=ft.FontWeight.BOLD),
                                            ft.Icon(icon=ft.Icons.MAP_ROUNDED, color=ft.Colors.TRANSPARENT,size=30),
                                        ]
                                    )
                                )
                            ),
                        ]
                    ),
                ]
            )
        )

  

    page.update()