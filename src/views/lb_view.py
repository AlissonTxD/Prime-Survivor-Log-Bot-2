from PyQt5.QtWidgets import QMainWindow

from src.core.viewmodels.log_bot_view_model import LogBotViewModel
from src.views.ui.log_bot_ui import Ui_MainWindow


class LogBotView(QMainWindow):
    def __init__(self):
        super().__init__()

        self.log_bot_vm = LogBotViewModel()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.btn_stop.setDisabled(True)

        self.ui.btn_start.clicked.connect(self.start_log_bot)
        self.ui.btn_stop.clicked.connect(self.stop_log_bot)

        self.load_ui()

    def start_log_bot(self):
        print("Iniciando Log Bot...")
        self.__save_config()

        resolution = self.ui.Combo_Resolution.currentText()
        coords = self.ui.Combo_Resolution.currentData()
        webhook = self.ui.LineEdit_webhook.text()
        identifier = self.ui.LineEdit_identifier.text()

        print("Resolution:", resolution)
        print("Coords:", coords)
        print("Webhook:", webhook)

        self.ui.btn_start.setDisabled(True)
        self.ui.btn_stop.setDisabled(False)

        self.log_bot_vm.start_log_bot(coords, webhook, identifier)

    def stop_log_bot(self):
        self.log_bot_vm.stop_log_bot()
        self.ui.btn_start.setDisabled(False)
        self.ui.btn_stop.setDisabled(True)

    def load_ui(self):
        self.config = self.log_bot_vm.config.load_config()

        for resolution, coords in self.config["resolution"].items():
            self.ui.Combo_Resolution.addItem(resolution, coords)

        self.last_resolution = self.config["last_resolution"]
        self.webhook = self.config["webhook"]
        self.identifier = self.config["identifier"]

        self.ui.LineEdit_identifier.setText(self.identifier)

        self.ui.Combo_Resolution.setCurrentText(self.last_resolution)

        self.ui.LineEdit_webhook.setText(self.webhook)

    def __save_config(self):
        self.config["last_resolution"] = self.ui.Combo_Resolution.currentText()
        self.config["webhook"] = self.ui.LineEdit_webhook.text()
        self.config["identifier"] = self.ui.LineEdit_identifier.text()
        self.log_bot_vm.config.save_config(self.config)