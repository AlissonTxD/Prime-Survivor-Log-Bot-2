import subprocess
from pathlib import Path

UI_FILE = Path(__file__).parent / "log_bot.ui"
PY_FILE = Path(__file__).parent / "log_bot_ui.py"


def converter_ui():
    comando = [
        "pyuic5",
        str(UI_FILE),
        "-o",
        str(PY_FILE)
    ]

    try:
        subprocess.run(comando, check=True)
        print("UI convertida com sucesso!")
        print(f"Entrada: {UI_FILE}")
        print(f"Saída:   {PY_FILE}")

    except subprocess.CalledProcessError as erro:
        print("Erro ao converter a UI.")
        print(erro)

    except FileNotFoundError:
        print("Erro: pyuic5 não foi encontrado.")
        print("Verifique se o ambiente virtual está ativado.")


if __name__ == "__main__":
    converter_ui()