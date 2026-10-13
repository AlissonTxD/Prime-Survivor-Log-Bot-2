import logging
import re

import cv2
import pytesseract

from .base_model import BaseModel

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_CONFIG = (
    "--oem 1 --psm 6 "
    "-c preserve_interword_spaces=1 "
    "-c load_system_dawg=0 -c load_freq_dawg=0"
)


class OcrModel(BaseModel):
    def read_img_ocr(self):
        try:
            img = cv2.imread(self.subimage_path)
            if img is None:
                raise FileNotFoundError(
                    f"Não foi possível abrir a imagem: {self.subimage_path}"
                )
            text = pytesseract.image_to_string(img, lang="eng", config=TESSERACT_CONFIG)
            text = text.replace("\r", "")
            text = re.sub(r"\s+", " ", text).strip()
            eventos = re.split(r"(?=Day\s+\d+)", text, flags=re.IGNORECASE)
            eventos = [evento.strip() for evento in eventos if evento.strip()]
            if eventos:
                return eventos[0]
            return ""

        except Exception as e:  # noqa: BLE001
            logging.error(f"Erro no OCR: {e}")  # noqa: LOG015
            return ""
