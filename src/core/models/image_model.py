import logging
import os

import cv2
import mss
import numpy as np
from PIL import Image

from .base_model import BaseModel

SCALE = 4          # fator de ampliação
BG_KERNEL = 7      # kernel (em px originais) maior que a espessura do traço
MIN_AREA = 28      # área mínima (px já ampliados) p/ manter um componente
PADDING = 20       # borda branca ao redor do texto
OCR_DPI = 300


def _ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def _remove_small_components(binary: np.ndarray, min_area: int) -> np.ndarray:
    """Remove ruídos pequenos (binary: texto = 255)."""
    n, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
    keep = np.zeros(n, dtype=np.uint8)
    keep[1:] = (stats[1:, cv2.CC_STAT_AREA] >= min_area).astype(np.uint8) * 255
    return keep[labels]


def preprocess_for_ocr(bgr: np.ndarray) -> np.ndarray:
    """Recebe imagem BGR e devolve imagem binária: texto preto em fundo branco."""
    # 1. Upscale
    img = cv2.resize(bgr, None, fx=SCALE, fy=SCALE, interpolation=cv2.INTER_CUBIC)

    # 2. Suavização leve (reduz ruído do fundo translúcido)
    img = cv2.GaussianBlur(img, (3, 3), 0)

    # 3. Estimar o fundo local (remove o texto e mantém o gradiente)
    k = int(BG_KERNEL * SCALE) | 1  # força ímpar
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))
    bg_light = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)   # fundo p/ texto claro
    bg_dark = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)   # fundo p/ texto escuro

    # 4. Diferença do texto em relação ao fundo, por canal, pegando o maior
    diff_light = np.max(cv2.subtract(img, bg_light), axis=2)
    diff_dark = np.max(cv2.subtract(bg_dark, img), axis=2)

    # 5. Escolhe a polaridade com mais "energia"
    if np.percentile(diff_light, 99) >= np.percentile(diff_dark, 99):
        diff = diff_light
    else:
        diff = diff_dark

    # 6. Normaliza, suaviza e binariza com Otsu (preserva melhor as bordas)
    diff = cv2.normalize(diff, None, 0, 255, cv2.NORM_MINMAX)
    diff = cv2.GaussianBlur(diff, (3, 3), 0)
    _, binary = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # 7. Remove pontinhos isolados
    binary = _remove_small_components(binary, MIN_AREA)

    # 8. Fechamento morfológico leve: fecha furos e junta traços quebrados
    close_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, close_k)

    # 9. Texto preto em fundo branco + borda
    result = cv2.bitwise_not(binary)
    result = cv2.copyMakeBorder(
        result, PADDING, PADDING, PADDING, PADDING, cv2.BORDER_CONSTANT, value=255
    )
    return result


class ImageModel(BaseModel):
    def generate_image_from_coords(self, cut_coords):
        try:
            with mss.mss() as sct:
                monitor_full = sct.monitors[1]  # monitor principal
                left = monitor_full["left"] + cut_coords[0]
                top = monitor_full["top"] + cut_coords[1]
                width = cut_coords[2] - cut_coords[0]
                height = cut_coords[3] - cut_coords[1]

                if width <= 0 or height <= 0:
                    raise ValueError("Coordenadas inválidas ou fora do monitor")

                shot = sct.grab(
                    {"left": left, "top": top, "width": width, "height": height}
                )

            # mss devolve BGRA -> descarta o alpha
            bgr = np.ascontiguousarray(np.array(shot)[:, :, :3])

            # Imagem original (antes de qualquer alteração)
            _ensure_parent_dir(self.main_image_path)
            Image.fromarray(bgr[:, :, ::-1]).save(self.main_image_path)  # BGR -> RGB
            logging.info(f"Imagem original salva em {self.main_image_path}")  # noqa: LOG015

            # Imagem processada para o OCR
            processed = preprocess_for_ocr(bgr)
            _ensure_parent_dir(self.subimage_path)
            Image.fromarray(processed).save(self.subimage_path, dpi=(OCR_DPI, OCR_DPI))
            logging.info(f"Imagem processada salva em {self.subimage_path}")  # noqa: LOG015

        except Exception as e:  # noqa: BLE001
            logging.error(f"Erro ao gerar imagem: {e}")  # noqa: LOG015