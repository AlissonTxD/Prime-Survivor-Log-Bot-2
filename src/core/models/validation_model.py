import logging
import re

from .base_model import BaseModel


class ValidationModel(BaseModel):

    def validate_log(self, text):
        try:
            match = re.match(
                r"Day (\d+), (\d{2}:\d{2}:\d{2}): (.*)",
                text,
                flags=re.IGNORECASE
            )

            if not match:
                logging.warning(  # noqa: LOG015
                    f"Invalid log format: {text}"
                )
                return False

            message = match.group(3)

            ignore_words = [
                "Baby",
                "Juvenile",
                "decay",
                "Karkinos"
            ]

            message_lower = message.lower()

            # Regra 1
            is_destroy_or_kill = (
                "your" in message_lower
                and (
                    "destroyed" in message_lower
                    or "killed" in message_lower
                )
                and not any(
                    word.lower() in message_lower
                    for word in ignore_words
                )
            )

            # Regra 2
            is_sensor = (
                "triggered" in message_lower
                and "enemy" in message_lower
            )

            if is_destroy_or_kill or is_sensor:
                self.log(f"Valid Event: {text}")
                return True

            self.log(f"Ignored Event: {text}")
            return False

        except Exception as e:  # noqa: BLE001
            logging.error(  # noqa: LOG015
                f"Erro validando log: {e}"
            )
            return False