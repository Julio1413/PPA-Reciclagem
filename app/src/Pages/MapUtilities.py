import asyncio
import platform
import requests

import flet as ft
import flet_geolocator as ftg


async def ObterLocalizacao(page: ft.Page):

    sistema = platform.system().lower()

    # =========================================================
    # WINDOWS / ANDROID / IOS
    # =========================================================

    if sistema in ("windows", "android", "ios"):

        geo = ftg.Geolocator(
            configuration=ftg.GeolocatorConfiguration(
                accuracy=ftg.GeolocatorPositionAccuracy.LOW
            )
        )

        # Adiciona o Geolocator à view atual
        page.views[-1].controls.append(geo)

        # IMPORTANTE:
        # Envia o controle para o cliente antes de invocar
        # seus métodos.
        page.update()

        # -----------------------------------------------------
        # Permissão
        # -----------------------------------------------------

        permissao = await geo.request_permission()

        if not permissao:
            raise RuntimeError(
                "Permissão de localização não concedida."
            )

        # -----------------------------------------------------
        # Localização
        # -----------------------------------------------------

        posicao = await geo.get_current_position()

        latitude = float(posicao.latitude)
        longitude = float(posicao.longitude)

        # -----------------------------------------------------
        # Cidade / Estado
        # -----------------------------------------------------

        cidade = None
        estado = None

        try:
            resposta = await asyncio.to_thread(
                requests.get,
                "https://nominatim.openstreetmap.org/reverse",
                params={
                    "lat": latitude,
                    "lon": longitude,
                    "format": "json",
                    "accept-language": "pt-BR",
                },
                headers={
                    "User-Agent": "PPA-Reciclagem/1.0"
                },
                timeout=5,
            )

            resposta.raise_for_status()

            endereco = resposta.json().get("address", {})

            cidade = (
                endereco.get("city")
                or endereco.get("town")
                or endereco.get("village")
                or endereco.get("municipality")
            )

            estado = endereco.get("state")

        except Exception:
            pass

        return {
            "latitude": latitude,
            "longitude": longitude,
            "cidade": cidade,
            "estado": estado,
        }

    # =========================================================
    # LINUX / MACOS / OUTROS
    # =========================================================

    try:

        resposta = await asyncio.to_thread(
            requests.get,
            "https://ipinfo.io/json",
            timeout=5
        )

        resposta.raise_for_status()

        dados = resposta.json()

        latitude, longitude = dados["loc"].split(",")

        return {
            "latitude": float(latitude),
            "longitude": float(longitude),
            "cidade": dados.get("city"),
            "estado": dados.get("region"),
        }

    except Exception as erro:

        raise RuntimeError(
            f"Não foi possível obter a localização por IP: {erro}"
        )