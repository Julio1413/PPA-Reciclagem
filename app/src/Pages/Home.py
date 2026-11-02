import asyncio
import flet as ft
import requests, math
from Pages import Ui, MapUtilities, MapView
from Ferramentas import Auth, Supabase

print('='*20)
print('Tela inicial')


#Funcoes auxiliares
def CalcularDistancia(coord1, coord2):
    """
    Recebe duas coordenadas (latitude, longitude)
    e retorna a distância entre elas em quilômetros.
    """

    lat1, lon1 = map(math.radians, coord1)
    lat2, lon2 = map(math.radians, coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    print(f'Distancia entre {coord1} e {coord2}: {6371 * c:.2f} km')
    return 6371 * c


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
    async def ObterLocalizacao():
        nonlocal loc
        loc = await MapUtilities.ObterLocalizacao(page)


    page.run_task(ObterLocalizacao)
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
    def Sheet(e,distancia):
        local = e.control.data


        def ReservarEMandarEmail():
            if Supabase.AtualizarLinha(
                nome_tabela='PontosColeta',
                filtros={'id': f"eq.{local['id']}"},
                novos_dados={'Reservado': 'True', 'ReservadoPor': Auth.ObterSessao()['email']},
            ):
                pass
            sheet.open = False
            page.update()


        sheet = ft.CupertinoBottomSheet(
            content=ft.Column(
                height=page.height * 0.785,
                spacing=10,
                controls=[
                    ft.Container(
                        margin=ft.Margin.only(left=10,right=10),
                        padding=0,
                        content=ft.Container(
                            border_radius=ft.BorderRadius.all(20),
                            bgcolor=Ui.ContainerColor(page=page,opacidade=0.5),
                            blur=(10, 10),
                            padding=15,
                            height=page.height * 0.6,
                            width=page.width,
                            margin=0,

                            content=ft.Column(
                                controls=[
                                    #Controles do dialogo
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(local["Titulo"], size=15, weight=ft.FontWeight.BOLD),
                                            ft.Icon(icon=ft.Icons.LOCATION_ON_ROUNDED, color=Ui.CorDeFundoSalva(), size=25),
                                        ]
                                    ),
                                    ft.Divider(),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(f'Latitude: {MapView._FormatarCoordenada(local["Latitude"])}', size=12),
                                            ft.Text(f'Longitude: {MapView._FormatarCoordenada(local["Longitude"])}', size=12),
                                        ]
                                    ),
                                    ft.Divider(),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(f'Distância: {distancia:.2f} km', size=12),
                                            ft.Text(f'ID: {local["id"]}', size=12),
                                        ]
                                    ),
                                    ft.Text(f'Autor: {local["NomeCriador"]}', size=12),
                                    ft.Divider(),
                                    ft.Text(local["Descrição"], size=12, selectable=True),
                                    #Conteúdo do dialogo

                                ]
                            )
                        )
                    ),


                    #Reservar e mandar e-mail
                    ft.Container(
                        on_click=lambda e: ReservarEMandarEmail(),
                        margin=ft.Margin.only(left=10,right=10),
                        padding=0,
                        content=ft.Container(
                            border_radius=ft.BorderRadius.all(20),
                            bgcolor=Ui.ContainerColor(page=page,opacidade=0.5),
                            blur=(10, 10),
                            padding=0,
                            height=50,
                            width=page.width,
                            margin=0,

                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text('Reservar e mandar e-mail',size=20),
                                ]
                            )
                        )
                    ),
                    #Cancelar
                    ft.Container(
                        on_click=lambda e: None,
                        margin=ft.Margin.only(left=10,right=10),
                        padding=0,
                        content=ft.Container(
                            border_radius=ft.BorderRadius.all(20),
                            bgcolor=Ui.ContainerColor(page=page,opacidade=0.5),
                            blur=(10, 10),
                            padding=0,
                            height=50,
                            width=page.width,
                            margin=0,

                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text('Cancelar',size=20),
                                ]
                            )
                        )
                    ),

                    
                ]
            )
        )
        
        page.overlay.append(sheet)
        sheet.open = True



    async def ObterLocalizacao():
        nonlocal loc
        loc = await MapUtilities.ObterLocalizacao(page)
        locais = Supabase.LerTabela('PontosColeta',{'Reservado': 'eq.False'})


        for local in locais:
            #Informações detalhadas


            distancia = CalcularDistancia(
                (float(local['Latitude']), float(local['Longitude'])),
                (float(loc['latitude']), float(loc['longitude']))
            )
            if distancia <= 1:
                colunalocais.controls.append(
                    ft.Container(
                        ink=True,
                        on_click=lambda e, distancia=distancia: Sheet(e, distancia),
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