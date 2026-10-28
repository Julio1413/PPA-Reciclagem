import flet as ft
import flet_map as ftm
from Pages import Ui, MapUtilities
from Ferramentas import Supabase
import requests


async def Mapa(page):
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
            content=ft.Icon(
                ft.Icons.LOCATION_PIN,
                color=Ui.CorDeFundoSalva(),
                size=30,
            ),
        )
        marcadores.append(marker)

    loc = await MapUtilities.ObterLocalizacao(page)
    print(loc)
    mapa = ftm.Map(
        min_zoom=15,
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
                        titulo='Mapa',
                        page=page,
                        icone=ft.Icons.MAP_ROUNDED,
                        icone_btn=ft.Icons.ARROW_BACK_IOS_ROUNDED,
                        destino='/'
                    ),
                    ft.Column(
                        alignment=ft.MainAxisAlignment.END,
                        height=page.height,
                        controls=[]
                    ),
                ])
            ]
        )
    )