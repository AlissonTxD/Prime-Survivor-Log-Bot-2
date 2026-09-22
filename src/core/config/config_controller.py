import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent / "config.json"


class ConfigController:
    def __init__(self):
        pass

    def load_config(self) -> dict:
        with open(CONFIG_FILE, "r", encoding="utf-8") as data:
            return json.load(data)

    def save_config(self, data: dict):
        with open(CONFIG_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
