import flet as ft
import flet_map as ftm
from Pages import Ui, MapUtilities
from Ferramentas import Supabase, Auth
import datetime


def _FormatarCoordenada(valor):
    texto = str(valor)
    resultado = []
    digitos = 0

    for caractere in texto:
        if caractere.isdigit():
            if digitos == 10:
                break
            digitos += 1

        resultado.append(caractere)

    return ''.join(resultado)


async def Mapa(page,titulo = 'Mapa Geral',marcadores=None, Adicionar_ponto=True):
    
    credenciais = Auth.ObterSessao()
    if not marcadores:
        marcadores_carregar = Supabase.LerTabela('PontosColeta', {'Reservado': 'eq.False'})
        print(marcadores_carregar)
        marcadores = []

    if marcadores_carregar is None:
        raise RuntimeError('Não foi possível carregar os pontos de coleta.')

    for marcador in marcadores_carregar:
        marcador_latitude = float(marcador['Latitude'])
        marcador_longitude = float(marcador['Longitude'])
        marker = ftm.Marker(
            coordinates=ftm.MapLatitudeLongitude(latitude=marcador_latitude, longitude=marcador_longitude),
            content=ft.Container(
                data=marcador,
                tooltip=marcador['Titulo'],
                on_click=lambda e: Ui.Sheet(e,page),
                ink=True,
                content=ft.Icon(
                    icon=ft.Icons.LOCATION_PIN,
                    color=Ui.CorDeFundoSalva(),
                    size=30
                )
            )
        )
        marcadores.append(marker)

    loc = await MapUtilities.ObterLocalizacao(page)

    




    #Selecionar e adicionar localização ao clicar no mapa
    def AbrirDialogo(longitude,latitude):
        def Salvar(e):
            if titulo.value and descricao.value:
                try:
                                
                    Supabase.InserirLinha(
                        'PontosColeta',
                        {   'EmailCriador': credenciais['email'],
                            'NomeCriador': credenciais['nome'],
                            'Titulo': titulo.value,
                            'Descrição': descricao.value,
                            'Latitude': latitude,
                            'Longitude': longitude,
                            'Reservado': 'False',
                            'ReservadoPor' : 'Ninguém',
                            'Criado': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'Finalizado': 'False',
                        }
                    )
                    Ui.IrPara('/',page)
                    Ui.IrPara('/mapa',page)
                    page.show_dialog(ft.SnackBar(ft.Text('Ponto de coleta adicionado com sucesso!'), open=True, bgcolor=ft.Colors.GREEN))
                    Cancelar(e)

                except:
                    page.show_dialog(ft.SnackBar(ft.Text('Erro ao adicionar ponto de coleta.'), open=True, bgcolor=ft.Colors.RED))
                    Cancelar(e)
            else:
                Cancelar(e)
                page.show_dialog(ft.SnackBar(ft.Text('Preencha todos os campos!'), open=True, bgcolor=ft.Colors.RED))


            

        def Cancelar(e):
            marcadores.pop(-1)
            sheet.open = False
            page.update()
        #sheet
        
        titulo = ft.TextField(label='Título',border_radius=10,width=page.width,keyboard_type=ft.KeyboardType.TEXT,border_color=ft.Colors.TRANSPARENT)

        descricao = ft.TextField(hint_text=' 1. Descreva o ponto de coleta;\n 2. Descreva os materiais disponíveis.',border_color=ft.Colors.TRANSPARENT,autocorrect=True,label='Descrição',multiline=True,keyboard_type=ft.KeyboardType.TEXT,width=page.width,border_radius=10,height=200)

        sheet = ft.CupertinoBottomSheet(
            on_dismiss=lambda e: Cancelar(e),
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
                            blur=(5, 5),
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
                                            ft.Text('Adicionar Ponto de Coleta', size=15, weight=ft.FontWeight.BOLD),
                                            ft.Icon(icon=ft.Icons.LOCATION_ON_ROUNDED, color=Ui.CorDeFundoSalva(), size=25),
                                        ]
                                    ),
                                    ft.Divider(),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[
                                            ft.Text(f'Latitude: {_FormatarCoordenada(latitude)}', size=12),
                                            ft.Text(f'Longitude: {_FormatarCoordenada(longitude)}', size=12),
                                        ]
                                    ),
                                    ft.Divider(),
                                    #Conteúdo do dialogo

                                    titulo,
                                    descricao,
                                ]
                            )
                        )
                    ),


                    #Salvar
                    ft.Container(
                        on_click=lambda e: Salvar(e),
                        margin=ft.Margin.only(left=10,right=10),
                        padding=0,
                        content=ft.Container(
                            border_radius=ft.BorderRadius.all(20),
                            bgcolor=Ui.ContainerColor(page=page,opacidade=0.5),
                            blur=(5, 5),
                            padding=0,
                            height=50,
                            width=page.width,
                            margin=0,

                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.CENTER,
                                controls=[
                                    ft.Text('Salvar',size=20),
                                ]
                            )
                        )
                    ),
                    #Cancelar
                    ft.Container(
                        on_click=lambda e: Cancelar(e),
                        margin=ft.Margin.only(left=10,right=10),
                        padding=0,
                        content=ft.Container(
                            border_radius=ft.BorderRadius.all(20),
                            bgcolor=Ui.ContainerColor(page=page,opacidade=0.5),
                            blur=(5, 5),
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
        #Tela para adicionar

        marcadores.append(
                    ftm.Marker(
                        coordinates=ftm.MapLatitudeLongitude(latitude=latitude, longitude=longitude),
                        content=ft.Icon(
                            ft.Icons.LOCATION_ON,
                            color=ft.Colors.RED,
                            size=35,
                        ),
                    )
                )
    
        page.update()
        
            


    def SelecionarLocal(e: ftm.MapTapEvent):
        lat = e.coordinates.latitude
        lon = e.coordinates.longitude
        print(f"Local selecionado: Latitude: {lat}, Longitude: {lon}")
        AbrirDialogo(lon,lat)
        page.update()



    def SelecionarSuaLocalicacao():
        AbrirDialogo(loc['longitude'],loc['latitude'])
        page.update()


    #Marcador de local
    marcadores.append(
        ftm.Marker(
            coordinates=ftm.MapLatitudeLongitude(latitude=loc['latitude'], longitude=loc['longitude']),
            content=ft.Stack(alignment=ft.Alignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.CIRCLE,
                        icon_color=Ui.CorDeFundoSalva(),
                        on_click=lambda e:SelecionarSuaLocalicacao(),
                        tooltip="Sua localização!",
                        scale=0.8
                    ),
                    
                   
                ]
            )
        )
    )




    mapa = ftm.Map(
        max_zoom=20,
        min_zoom=15,
        on_long_press=SelecionarLocal if Adicionar_ponto else None,
        initial_zoom=15,
        expand=True,
        layers=[
            ftm.TileLayer(
                url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                user_agent_package_name="flet-map-examples/1.0",
                on_image_error=lambda e: print(f"TileLayer Error: {e.data}"),
            ),
            ftm.MarkerLayer(
                markers=marcadores
            ),
            ftm.SimpleAttribution(text="OpenStreetMap contributors",bgcolor=ft.Colors.TRANSPARENT,text_style=ft.TextStyle(color=ft.Colors.BLACK, size=10)),

        ],
    )
    mapa.initial_center = ftm.MapLatitudeLongitude(
        latitude=loc['latitude'],
        longitude=loc['longitude'],
    )

    def PontoZero():
        
        
        async def _MoverEAplicarZoom():
            await mapa.zoom_to(zoom=15)
            await mapa.move_to(
                destination=ftm.MapLatitudeLongitude(
                    latitude=loc['latitude'],
                    longitude=loc['longitude'],
                )
            )

        page.run_task(_MoverEAplicarZoom)


    page.views.append(
        ft.View(
            route='/mapa',
            bgcolor=Ui.CorDeFundoSalva(),
            controls=[
                ft.Stack([
                    ft.Container(
                        padding=-10,
                        width=page.width,
                        height=page.height *0.973,
                        content=mapa
                    ),
                    Ui.Cabecalho(
                        titulo=titulo,
                        page=page,
                        icone=ft.Icons.MAP_ROUNDED,
                        icone_btn=ft.Icons.ARROW_BACK_IOS_ROUNDED,
                        destino='/'
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.END,
                        horizontal_alignment= ft.CrossAxisAlignment.END,
                        height=page.height,
                        controls=[
                            ft.Container(
                                ink=True,
                                on_click=lambda _:PontoZero(),
                                bgcolor=Ui.ContainerColor(page=page,opacidade=0.5),
                                blur=(5,5),
                                border_radius=20,
                                padding=10,
                                content=ft.Icon(
                                    icon=ft.Icons.MY_LOCATION_ROUNDED,
                                    size=25,
                                    color=Ui.TextColor(page)
                                )
                            ),

                            ft.Placeholder(height=25,color=ft.Colors.TRANSPARENT)
                        ]
                    ),
                ])
            ]
        )
    )