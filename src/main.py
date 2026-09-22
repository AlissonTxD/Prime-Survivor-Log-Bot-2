import logging
import sys

from PyQt5.QtWidgets import QApplication

from src.views.lb_view import LogBotView

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def start():
    print("Starting the application...")
    app = QApplication(sys.argv)
    window = LogBotView()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    start()