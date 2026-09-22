import logging
import os

import mss
from PIL import Image, ImageEnhance

from .base_model import BaseModel

IMG_FACTORS = (2.0, 0.5, 1.0, 2.5)


class ImageModel(BaseModel):
    def generate_image_from_coords(self, cut_coords):
        print(cut_coords)
        print(cut_coords[0])
        print(type(cut_coords[0]))
        try:
            os.makedirs("temp", exist_ok=True)

            with mss.mss() as sct:
                monitor_full = sct.monitors[1]  # monitor principal
                left = monitor_full["left"] + cut_coords[0]
                top = monitor_full["top"] + cut_coords[1]
                width = cut_coords[2] - cut_coords[0]
                height = cut_coords[3] - cut_coords[1]

                if width <= 0 or height <= 0:
                    raise ValueError("Coordenadas inválidas ou fora do monitor")

                monitor = {"left": left, "top": top, "width": width, "height": height}
                screenshot = sct.grab(monitor)

                mss.tools.to_png(
                    screenshot.rgb, screenshot.size, output=self.subimage_path
                )

            # Ajustes de imagem para OCR
            img = Image.open(self.subimage_path).convert("RGB")
            img = ImageEnhance.Contrast(img).enhance(IMG_FACTORS[0])
            img = ImageEnhance.Color(img).enhance(IMG_FACTORS[1])
            img = ImageEnhance.Brightness(img).enhance(IMG_FACTORS[2])
            img = ImageEnhance.Sharpness(img).enhance(IMG_FACTORS[3])
            img = img.resize((img.width * 2, img.height * 2), Image.LANCZOS)
            img.save(self.subimage_path)

            logging.info(f"Imagem gerada em {self.subimage_path}")  # noqa: LOG015

        except Exception as e:  # noqa: BLE001
            logging.error(f"Erro ao gerar imagem: {e}")  # noqa: LOG015
