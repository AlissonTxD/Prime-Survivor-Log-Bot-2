import logging


class BaseModel:
    def __init__(self):
        self.subimage_path = "temp/subimage.png"
        self.main_image_path = "temp/main_image.png"

    def log(self, msg):
        logging.info(msg)  # noqa: LOG015
