import re
import threading

from src.core.config.config_controller import ConfigController
from src.core.models.discord_model import DiscordModel
from src.core.models.image_model import ImageModel
from src.core.models.ocr_model import OcrModel
from src.core.models.validation_model import ValidationModel

CHECK_INTERVAL_SECONDS = 15


class LogBotViewModel:
    def __init__(self):
        self.__load_models()

        self.event_counter = 0
        self.reset_counter = 0
        self.events = []
        self.testmode = None

        self.stop_event = threading.Event()
        self.log_bot_thread = None

    def start_log_bot(self, cutcoords, api):

        # Garante que um novo Start possa iniciar novamente
        self.stop_event.clear()

        self.log_bot_thread = threading.Thread(
            target=self.run, args=(cutcoords, api), daemon=True
        )

        self.log_bot_thread.start()

    def run(self, coords, webhook):

        loops_for_minute = 60 // CHECK_INTERVAL_SECONDS

        self.discord = DiscordModel(webhook)
        self.discord.config_webhook_profile()

        while not self.stop_event.is_set():
            self.image.generate_image_from_coords(coords)

            text = self.ocr.read_img_ocr()

            if self.validation.validate_log(text):
                if self.__validade_new(text):
                    message = f"# {text}"

                    if self.event_counter > 5:
                        message = f"# @everyone {text}"

                    elif self.event_counter >= 3:
                        message = f"# @here {text}"

                    self.discord.send_msg(message)

                    self.event_counter += 1
                    self.reset_counter = loops_for_minute * 10

                else:
                    print("valido mas nao é novo")

            else:
                print("nao valido")

            self.reset_counter += 1

            if self.reset_counter >= (loops_for_minute * 20):
                self.event_counter = 0
                self.reset_counter = 0

            # Espera o próximo ciclo.
            # Se Stop for pressionado, a espera é interrompida imediatamente.
            if self.stop_event.wait(CHECK_INTERVAL_SECONDS):
                break

        print("Log Bot parado.")

    def stop_log_bot(self):

        print("Parando Log Bot...")

        self.stop_event.set()

        if self.log_bot_thread is not None:
            self.log_bot_thread.join(timeout=2)
        self.reset_counter = 0
        self.event_counter = 0
        self.events = []
        self.log_bot_thread = None

    def __load_models(self):
        self.config = ConfigController()
        self.image = ImageModel()
        self.ocr = OcrModel()
        self.validation = ValidationModel()

    def __validade_new(self, text) -> bool:
        match = re.match(
            r"Day (\d+), (\d{2}:\d{2}:\d{2}): (.*)", text, flags=re.IGNORECASE
        )
        if not match:
            return False

        day = match.group(1)
        hour = match.group(2)
        event_id = f"{day} {hour}"

        if event_id not in self.events:
            self.events.append(event_id)
            print(self.events)
            return True

        print("evento ja registrado")
        print(self.events)
        return False
