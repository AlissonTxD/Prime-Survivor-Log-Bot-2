from PyQt5.QtWidgets import QMainWindow

from src.views.ui.log_bot_ui import Ui_MainWindow


class LogBotView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_stop.setDisabled(True)