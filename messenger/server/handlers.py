import configparser
import os
import sys
import threading
from server import parse_args, Server
from db.repository import Repository
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, \
    create_stat_model, ConfigWindow

conflag_lock = threading.Lock()


class Console:
    def __init__(self, args):
        self.__server = Server((args.a, args.p), Repository())
        pass

    def main(self):
        self.__server.run()


class Gui:
    def main(self):
        config = configparser.ConfigParser()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        config.read(f"{dir_path}/{'server.ini'}")
        result = parse_args(
            default_ip=config['SETTINGS']['listen_address'],
            default_port=config['SETTINGS']['default_port']
        )
        listen_address = result.a
        listen_port = result.p

        database = Repository(
            os.path.join(config['SETTINGS']['Database_path'] or dir_path,
                         config['SETTINGS']['Database_file']))

        server = Server((listen_address, listen_port), database)
        server.handler = self
        server.daemon = True
        server.start()

        server_app = QApplication(sys.argv)
        main_window = MainWindow()

        main_window.statusBar().showMessage('Server Working')
        main_window.active_clients_table.setModel(gui_create_model(database))
        main_window.active_clients_table.resizeColumnsToContents()
        main_window.active_clients_table.resizeRowsToContents()

        def list_update():
            if server.new_connection:
                main_window.active_clients_table.setModel(gui_create_model(database))
                main_window.active_clients_table.resizeColumnsToContents()
                main_window.active_clients_table.resizeRowsToContents()
                with conflag_lock:
                    server.new_connection = False

        def show_statistics():
            global stat_window
            stat_window = HistoryWindow()
            stat_window.history_table.setModel(create_stat_model(database))
            stat_window.history_table.resizeColumnsToContents()
            stat_window.history_table.resizeRowsToContents()
            stat_window.show()

        def server_config():
            global config_window
            config_window = ConfigWindow()
            config_window.db_path.insert(config['SETTINGS']['Database_path'])
            config_window.db_file.insert(config['SETTINGS']['Database_file'])
            config_window.port.insert(config['SETTINGS']['default_port'])
            config_window.ip.insert(config['SETTINGS']['listen_address'])
            config_window.save_btn.clicked.connect(save_server_config)

        def save_server_config():
            global config_window
            message = QMessageBox()
            config['SETTINGS']['Database_path'] = config_window.db_path.text()
            config['SETTINGS']['Database_file'] = config_window.db_file.text()
            try:
                port = int(config_window.port.text())
            except ValueError:
                message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
            else:
                config['SETTINGS']['listen_address'] = config_window.ip.text()
                if 1023 < port < 65536:
                    config['SETTINGS']['default_port'] = str(port)
                    print(port)
                    with open(os.path.join(dir_path, 'server.ini'), 'w') as conf:
                        config.write(conf)
                        message.information(config_window, 'OK',
                                            'Настройки успешно сохранены!')
                else:
                    message.warning(config_window, 'Ошибка',
                                    'Порт должен быть от 1024 до 65536')

        timer = QTimer()
        timer.timeout.connect(list_update)
        timer.start(1000)

        main_window.refresh_button.triggered.connect(list_update)
        main_window.show_history_button.triggered.connect(show_statistics)
        main_window.config_btn.triggered.connect(server_config)

        server_app.exec_()
