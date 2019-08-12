import sys
import time

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication, QLabel, \
    QTableView, QDialog, QPushButton, QLineEdit, QFileDialog, QMessageBox, \
    QComboBox


def gui_create_model(database):
    """
    Функция, заполняющяя таблицу активных пользователей.
    :param database: БД
    :return:
    """
    while True:
        try:
            list_users = database.users_list(active=True)
            qt_list = QStandardItemModel()
            qt_list.setHorizontalHeaderLabels(
                ['Имя Клиента', 'Время подключения', 'IP Адрес'])
            for user_name in list_users:
                row = database.login_history(user_name)[-1]
                name, date_time, ip = row
                user = QStandardItem(name)
                user.setEditable(False)
                ip = QStandardItem(ip)
                ip.setEditable(False)
                date_time = QStandardItem(str(date_time))
                date_time.setEditable(False)
                qt_list.appendRow([user, date_time, ip])
        except Exception:
            time.sleep(1)
            continue
        else:
            return qt_list


def create_stat_model(database):
    """
    Функция, реализующяя заполнение таблицы статистикой сообщений.
    :param database:
    :return:
    """
    hist_list = database.message_history()

    qt_list = QStandardItemModel()
    qt_list.setHorizontalHeaderLabels([
        'Имя Клиента', 'Последний раз входил', 'Сообщений отправлено',
        'Сообщений получено'
    ])
    for row in hist_list:
        user, last_seen, sent, recvd = row
        user = QStandardItem(user)
        user.setEditable(False)
        if last_seen:
            last_seen = QStandardItem(str(last_seen.replace(microsecond=0)))
        else:
            last_seen = QStandardItem('')
        last_seen.setEditable(False)
        sent = QStandardItem(str(sent))
        sent.setEditable(False)
        recvd = QStandardItem(str(recvd))
        recvd.setEditable(False)
        qt_list.appendRow([user, last_seen, sent, recvd])
    return qt_list


class MainWindow(QMainWindow):
    """
    Класс - основное окно сервера.
    """
    def __init__(self):
        super().__init__()
        exit_action = QAction('Выход', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(qApp.quit)

        self.refresh_button = QAction('Обновить список', self)
        self.config_btn = QAction('Настройки сервера', self)
        self.show_history_button = QAction('История клиентов', self)
        self.remove_btn = QAction('Удаление пользователя', self)
        self.statusBar()

        self.toolbar = self.addToolBar('MainBar')
        self.toolbar.addAction(exit_action)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_history_button)
        self.toolbar.addAction(self.config_btn)
        self.toolbar.addAction(self.remove_btn)

        self.setFixedSize(800, 600)
        self.setWindowTitle('Messaging Server alpha release')

        self.label = QLabel('Список подключённых клиентов:', self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        self.show()


class HistoryWindow(QDialog):
    """
    Класс - окно с историей пользователей
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Статистика клиентов')
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.history_table = QTableView(self)
        self.history_table.move(10, 10)
        self.history_table.setFixedSize(580, 620)

        self.show()


class ConfigWindow(QDialog):
    """
    Класс окно настроек.
    """
    def __init__(self):
        super().__init__()
        self.setFixedSize(365, 260)
        self.setWindowTitle('Настройки сервера')

        self.db_path_label = QLabel('Путь до файла базы данных: ', self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton('Обзор...', self)
        self.db_path_select.move(275, 28)

        self.dialog = None

        self.db_path_select.clicked.connect(self.open_file_dialog)

        self.db_file_label = QLabel('Имя файла базы данных: ', self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel('Номер порта для соединений:', self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel('С какого IP принимаем соединения:', self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel(
            ' оставьте это поле пустым, '
            'чтобы\n принимать соединения с любых адресов.',
            self)
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_btn = QPushButton('Сохранить', self)
        self.save_btn.move(190, 220)

        self.close_button = QPushButton('Закрыть', self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()

    def open_file_dialog(self):
        """
        Метод обработчик открытия окна выбора папки.
        :return:
        """
        self.dialog = QFileDialog(self)
        path = self.dialog.getExistingDirectory()
        path = path.replace('/', '\\')
        self.db_path.insert(path)


class DelUserDialog(QDialog):
    """
    Класс - диалог выбора контакта для удаления.
    """
    def __init__(self):
        super().__init__()

        self.setFixedSize(350, 120)
        self.setWindowTitle('Удаление пользователя')
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel('Выберите пользователя для удаления:',
                                     self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_ok = QPushButton('Удалить', self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton('Отмена', self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    message = QMessageBox
    dial = ConfigWindow()

    app.exec_()
