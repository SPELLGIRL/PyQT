import configparser
import sys
import threading

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QMessageBox

from db.repository import Repository
from server import parse_args, Server
from server_gui import MainWindow, gui_create_model, HistoryWindow, \
    create_stat_model, ConfigWindow, DelUserDialog
from settings import *


def config_load():
    """
    Парсер конфигурационного ini файла.
    :return:
    """
    config = configparser.ConfigParser()
    config.read(f"{DIR_PATH}/{'server.ini'}")
    # Если конфиг файл загружен правильно, запускаемся,
    # иначе конфиг по умолчанию.
    if 'SETTINGS' in config:
        return config
    else:
        config.add_section('SETTINGS')
        config.set('SETTINGS', 'Default_port', str(DEFAULT_PORT))
        config.set('SETTINGS', 'Listen_Address', str(DEFAULT_IP))
        config.set('SETTINGS', 'Database_path', '')
        config.set('SETTINGS', 'Database_file', 'server.db')
        return config


DIR_PATH = os.path.dirname(os.path.realpath(__file__))
conflag_lock = threading.Lock()
config = config_load()


class Console:
    """
    Класс обработчика для консольного режима
    """
    def __init__(self):
        args = parse_args(default_ip=config['SETTINGS']['listen_address'],
                          default_port=config['SETTINGS']['default_port'])
        self.__server = Server((args.a, args.p), Repository())

    def main(self):
        """
        Метод, запускающий консольный сервер
        :return:
        """
        self.__server.run()


class Gui:
    """
    Класс обработчика для графического режима
    """
    def __init__(self):
        args = parse_args(default_ip=config['SETTINGS']['listen_address'],
                          default_port=config['SETTINGS']['default_port'])
        self.database = Repository(config['SETTINGS']['Database_path'],
                                   config['SETTINGS']['Database_file'])
        self.server = Server((args.a, args.p), self.database)
        self.server.handler = self
        self.server.daemon = True

        self.server_app = QApplication(sys.argv)

        self.main_window = MainWindow()
        self.main_window.statusBar().showMessage('Server Working')
        self.main_window.active_clients_table.setModel(
            gui_create_model(self.database))
        self.main_window.active_clients_table.resizeColumnsToContents()
        self.main_window.active_clients_table.resizeRowsToContents()
        self.main_window.refresh_button.triggered.connect(self.list_update)
        self.main_window.show_history_button.triggered.connect(
            self.show_statistics)
        self.main_window.config_btn.triggered.connect(self.server_config)
        self.main_window.remove_btn.triggered.connect(self.remove_user_dialog)

        self.stat_window = None
        self.rm_user_window = None
        self.config_window = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.list_update)

    def main(self):
        """
        Метод, запускающий графическую оболочку и необходимые компоненты
        :return:
        """
        self.server.start()
        self.timer.start(1000)
        self.server_app.exec_()

    def list_update(self):
        """
        Метод, обновляющий список подключённых клиентов
        :return:
        """
        if self.database.new_connection:
            self.main_window.active_clients_table.setModel(
                gui_create_model(self.database))
            self.main_window.active_clients_table.resizeColumnsToContents()
            self.main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                self.database.new_connection = False

    def show_statistics(self):
        """
        Метод создающий окно со статистикой клиентов.
        :return:
        """
        self.stat_window = HistoryWindow()
        self.stat_window.history_table.setModel(
            create_stat_model(self.database))
        self.stat_window.history_table.resizeColumnsToContents()
        self.stat_window.history_table.resizeRowsToContents()
        self.stat_window.show()

    def remove_user_dialog(self):
        """
        Метод, создающий окно удаления пользователя.
        :return:
        """
        self.rm_user_window = DelUserDialog()
        self.rm_user_window.selector.addItems(
            [item for item in self.database.users_list()])
        self.rm_user_window.btn_ok.clicked.connect(self.remove_user)

    def remove_user(self):
        """
        Метод, запускающий процесс удаления пользователя.
        :return:
        """
        user_name = self.rm_user_window.selector.currentText()
        self.database.remove_user(user_name)
        self.server.remove_client_by_name(user_name)
        self.rm_user_window.close()

    def server_config(self):
        """
        Метод создающий окно с настройками сервера.
        :return:
        """
        self.config_window = ConfigWindow()
        self.config_window.db_path.insert(config['SETTINGS']['Database_path'])
        self.config_window.db_file.insert(config['SETTINGS']['Database_file'])
        self.config_window.port.insert(config['SETTINGS']['default_port'])
        self.config_window.ip.insert(config['SETTINGS']['listen_address'])
        self.config_window.save_btn.clicked.connect(self.save_server_config)

    def save_server_config(self):
        """
        Метод проверки и сохранения настроек сервера.
        :return:
        """
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = self.config_window.db_path.text()
        config['SETTINGS']['Database_file'] = self.config_window.db_file.text()
        try:
            port = int(self.config_window.port.text())
        except ValueError:
            message.warning(self.config_window, 'Ошибка',
                            'Порт должен быть числом')
        else:
            config['SETTINGS']['listen_address'] = self.config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['default_port'] = str(port)
                with open(os.path.join(DIR_PATH, 'server.ini'), 'w') as conf:
                    config.write(conf)
                    message.information(self.config_window, 'OK',
                                        'Настройки успешно сохранены!')
            else:
                message.warning(self.config_window, 'Ошибка',
                                'Порт должен быть от 1024 до 65536')
