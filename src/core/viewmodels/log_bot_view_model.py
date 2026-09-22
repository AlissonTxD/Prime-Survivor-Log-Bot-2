import threading
from time import sleep

from src.core.config.config_controller import ConfigController
from src.core.models.discord_model import DiscordModel
from src.core.models.image_model import ImageModel
from src.core.models.ocr_model import OcrModel
from src.core.models.validation_model import ValidationModel


class LogBotViewModel:
    def __init__(self):
        self.__load_models()

    def start_log_bot(self, cutcoords, api):
        log_bot_thread = threading.Thread(
            target=self.run, args=(cutcoords, api), daemon=True
        )

        log_bot_thread.start()

    def run(self, coords, webhook):
        self.discord = DiscordModel(webhook)
        self.discord.config_webhook_profile()
        sleep(5)
        self.image.generate_image_from_coords(coords)
        text = self.ocr.read_img_ocr()
        if self.validation.validate_log(text):
            self.discord.send_msg(text)
        else:
            print("nao importa")
            
    def stop_log_bot(self):
        pass

    def __load_models(self):
        self.config = ConfigController()
        self.image = ImageModel()
        self.ocr = OcrModel()
        self.validation = ValidationModel()
