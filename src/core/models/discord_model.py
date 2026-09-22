import base64
import logging

import requests

from .base_model import BaseModel


class DiscordModel(BaseModel):
    def __init__(self, webhook_url):
        super().__init__()

        self.webhook_url = webhook_url
        self.webhook_name = "Prime Survivor Log Bot"
        self.avatar_path = "src/assets/log_bot_logo.png"

    def config_webhook_profile(self):
        try:
            with open(self.avatar_path, "rb") as file:
                image = file.read()

            image_base64 = base64.b64encode(image).decode("utf-8")

            response = requests.patch(
                self.webhook_url,
                json={
                    "name": self.webhook_name,
                    "avatar": (f"data:image/png;base64,{image_base64}"),
                },
            )

            response.raise_for_status()

            self.log("Perfil do webhook configurado.")

            return True

        except Exception as e:  # noqa: BLE001
            logging.error(  # noqa: LOG015
                f"Erro ao configurar webhook: {e}"
            )
            return False

    def send_msg(self, text):
        try:
            # Envia a mensagem
            response = requests.post(
                self.webhook_url,
                json={"content": text},
            )

            response.raise_for_status()

            self.log("Mensagem enviada para o Discord.")

            # Envia a imagem do log
            with open(self.subimage_path, "rb") as image:
                response = requests.post(
                    self.webhook_url,
                    files={"file": ("subimage.png", image, "image/png")},
                )

            response.raise_for_status()

            self.log("Imagem enviada para o Discord.")

            return True

        except Exception as e:  # noqa: BLE001
            logging.error(  # noqa: LOG015
                f"Erro ao enviar mensagem para o Discord: {e}"
            )
            return False
