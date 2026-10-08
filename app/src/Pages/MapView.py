import flet as ft
import flet_map as ftm
from Pages import Ui, MapUtilities
import requests


async def Mapa(page):
    
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
                markers=[
                    ftm.Marker(
                        coordinates=ftm.MapLatitudeLongitude(latitude=loc['latitude'],longitude=loc['longitude']),
                        content=ft.Icon(
                            ft.Icons.LOCATION_PIN,
                            color=Ui.CorDeFundoSalva(),
                            size=30,
                        ),
                    )
                ]
            ),
            #ftm.SimpleAttribution(text="OpenStreetMap contributors"),

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