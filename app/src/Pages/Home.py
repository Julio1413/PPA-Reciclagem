import asyncio
import flet as ft
import requests
from Pages import Ui, MapUtilities, MapView
from Ferramentas import Auth, Supabase, Ferramentas


print('='*20)
print('Tela inicial')


#Funcoes auxiliares



def ObtercidadeIp():
    resposta = requests.get("http://ip-api.com/json/", timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()
 
    if dados.get("status") != "success":
        return None
 
    return dados
 
#Pagina inicial
def Inicio (page):
    #Serviço de localização
    loc = None
 
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



    #Locais proximos

    colunalocais = ft.Column(scroll=ft.ScrollMode.AUTO,expand=True,controls=[])


    loc = None
    


    async def ObterLocalizacao():
        nonlocal loc
        loc = await MapUtilities.ObterLocalizacao(page)
        locais = Supabase.LerTabela('PontosColeta',{'Reservado': 'eq.False'})
        colunalocais.controls.clear()

        for local in locais:
            #Informações detalhadas


            distancia = Ferramentas.CalcularDistancia(
                (float(local['Latitude']), float(local['Longitude'])),
                (float(loc['latitude']), float(loc['longitude']))
            )
            if distancia <= 1:
                colunalocais.controls.append(
                    ft.Container(
                        ink=True,
                        on_click=lambda e, distancia=distancia: Ui.Sheet(
                            e, page, distancia=distancia
                        ),
                        data=local,
                        width=page.width,
                        padding=10,
                        border_radius=12,
                        bgcolor=ft.Colors.with_opacity(0.15, ft.Colors.GREY),
                        content=ft.Column(
                            controls=[
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    controls=[
                                        ft.Text(local['Titulo'],size=17,weight=ft.FontWeight.BOLD),
                                        ft.Text(f'{distancia:.2f} km',size=15),
                                    ]
                                ),
                                ft.Text(local['Descrição'],size=12),
                            ]
                        )
                    )
                )
            page.update()
                

    
    page.run_task(ObterLocalizacao)



    #Construção da página
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
                                            ft.Icon(icon=ft.Icons.STICKY_NOTE_2_ROUNDED, color=ft.Colors.WHITE,size=30),
                                            ft.Text('Minha atividade',color=ft.Colors.WHITE,size=20,weight=ft.FontWeight.BOLD),
                                            ft.Icon(icon=ft.Icons.MAP_ROUNDED, color=ft.Colors.TRANSPARENT,size=30),
                                        ]
                                    )
                                )
                            ),
                            ft.Placeholder(color=ft.Colors.TRANSPARENT, height=10),
                            ft.Text('Pontos em um raio de 1 Km'),
                            ft.Divider(),
                            colunalocais,
                        ]
                    ),
                ]
            )
        )

  

    page.update()