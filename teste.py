import flet as ft
import flet_map as ftm
import requests


def obter_localizacao():
    resposta = requests.get(
        "https://ipinfo.io/json",
        timeout=5
    )
    resposta.raise_for_status()

    latitude, longitude = resposta.json()["loc"].split(",")

    return {'latitude' :float(latitude), 'longitude':float(longitude)}

def main(page: ft.Page):


    loc = obter_localizacao()
    page.add(
        ft.SafeArea(
            expand=True,
            content=ftm.Map(
                initial_center=ftm.MapLatitudeLongitude(
                    latitude=loc['latitude'],
                    longitude=loc['longitude'],
                ),
                initial_zoom=20,
                expand=True,
                layers=[
                    ftm.TileLayer(
                        url_template="https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                        user_agent_package_name="flet-map-examples/1.0",
                        on_image_error=lambda e: print(f"TileLayer Error: {e.data}"),
                    ),
                    ftm.SimpleAttribution(text="OpenStreetMap contributors"),
                ],
            ),
        )
    )


if __name__ == "__main__":
    ft.run(main)