import socket
import sys
from random import randint
from threading import Thread, Lock

from Crypto.Cipher import PKCS1_OAEP
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QMessageBox

from jim.config import *
from jim.utils import Message, receive
from .client import Client, log_decorator
from .client_gui import ClientMainWindow, UserNameDialog
from .db.repository import Repository
from .exceptions import *

socket_lock = Lock()


class Console:
    """Класс обработчика для консольного режима."""
    __slots__ = ('__client', '__actions', '__listen_thread', '__repo')

    def __init__(self, parsed_args):
        self.__client = Client((parsed_args.addr, parsed_args.port))
        self.__client.user_name, self.__client.password = \
            self.__validate_username(parsed_args.user, parsed_args.password)
        self.__repo = Repository(self.__client.user_name)
        self.__listen_thread = Thread(target=self.receiver)
        self.__listen_thread.daemon = True

        self.__actions = (
            {
                ACTION: 'exit',
                'name': 'Выйти',
            },
            {
                ACTION: SEND_MSG,
                'name': 'Отправить сообщение(* - всем)',
                'params': (
                    TO,
                    TEXT,
                )
            },
            {
                ACTION: GET_CONTACTS,
                'name': 'Запросить список контактов',
            },
            {
                ACTION: ADD_CONTACT,
                'name': 'Добавить контакт',
                'params': (USER, ),
            },
            {
                ACTION: DEL_CONTACT,
                'name': 'Удалить контакт',
                'params': (USER, ),
            },
            {
                ACTION: 'help',
                'name': 'Справка',
            },
        )

    @staticmethod
    def __validate_username(user_name: str, password: str) -> tuple:
        """
        Метод проверки корректности введенных имени и пароля.
        :param user_name: Имя клиента
        :param password: Пароль клиента
        :return: Кортеж логин, пароль.
        """
        while True:
            if user_name == 'Гость' or not user_name:
                user_name = input('Введите своё имя: ') or \
                            f'Гость_{randint(1, 9999)}'
                user_name = user_name.strip()
                try:
                    if len(user_name) > 25:
                        raise UsernameToLongError
                except UsernameToLongError as ce:
                    print(ce)
                    exit(0)
            else:
                break
        if not password:
            password = input('Введите пароль: ')
        return user_name, password

    @log_decorator
    def interact(self) -> Message:
        """
        Метод взаимодействия с пользователем.
        :return:
        """
        while True:
            try:
                params = {}
                num = abs(int(input('Выберите действие: ')))
                if 0 <= num <= len(self.__actions):
                    start = self.__actions[num]
                else:
                    raise ValueError
                if start[ACTION] == 'exit':
                    raise KeyboardInterrupt
                elif start[ACTION] == 'help':
                    print(self.__help_info)
                    continue
                params = {ACTION: start[ACTION]}
                if 'params' in start:
                    for param in start['params']:
                        p = str(input(f'Выберите параметр "{param}": '))
                        params[param] = p
                if start[ACTION] == ADD_CONTACT:
                    self.__repo.add_contact(params[USER])
                elif start[ACTION] == DEL_CONTACT:
                    self.__repo.del_contact(params[USER])
                elif start[ACTION] == SEND_MSG:
                    if params[TO] == '' or params[TO] == '*':
                        to = ', '.join(self.__repo.get_contacts())
                    else:
                        to = params[TO]
                    self.__repo.save_message(to, "out", params[TEXT])
                break
            except ValueError:
                print('Действие не распознано, попробуйте еще раз...')
                pass
        return Message(**params)

    @property
    def __help_info(self):
        """
        Метод, отображающий возможные действия.
        :return:
        """
        return '\n'.join([
            f'{key}. {action["name"]}'
            for key, action in enumerate(self.__actions, 0)
        ])

    def key_request(self, user_name: str) -> str:
        """
        Метод получающий открытый ключ контакта с сервера.
        :param user_name: Имя контакта
        :return:
        """
        data = {
            ACTION: PUBLIC_KEY_REQUEST,
            FROM: self.__client.user_name,
            USER: user_name
        }
        with socket_lock:
            self.__client.send(Message(**data))
            responses = receive(self.__client.sock, self.__client.logger)
            if responses:
                response = responses[0]
                if response.response and response.text:
                    return response.text
            self.__client.logger.error(
                f'Не удалось получить ключ собеседника{user_name}.')

    def main(self):
        """
        Главный метод, запускающий необходимые компоненты.
        :return:
        """
        action = self.__client.connect()
        if not action:
            raise ConnectionResetError
        if not self.__client.auth(action):
            raise ServerError('Неправильный пароль.')
        self.__repo.clear_contacts()
        for message in self.__client.load_contacts()[1:]:
            self.__repo.add_contact(message.user)
        try:
            self.__listen_thread.start()
            print(self.__help_info)
            while True:
                message = self.interact()
                self.__client.send(message)
        except KeyboardInterrupt:
            print('Клиент закрыт по инициативе пользователя.')
        except ConnectionResetError:
            print('Соединение с сервером разорвано.')
        except ConnectionAbortedError:
            print('Пользователь с таким именем уже подключён. '
                  'Соединение с сервером разорвано.')
        except CUSTOM_EXCEPTIONS as ce:
            print(ce)
        finally:
            self.__listen_thread.is_alive = False
            self.__client.close()

    def receiver(self, flag=1):
        """
        Метод запускающий получение и обработку сообщений.
        Работает в отдельном потоке.
        :param flag: Если передана не 1, то выполнит только 1 цикл.
        :return:
        """
        try:
            while True:
                messages = []
                try:
                    messages = receive(self.__client.sock,
                                       self.__client.logger)
                except socket.timeout:
                    pass
                while len(messages):
                    message = messages.pop()
                    checked_msg = self.__client.check_response(message)
                    self.receive_callback(checked_msg)
                if flag != 1:
                    break
        except ConnectionResetError:
            self.__listen_thread.is_alive = False

    def receive_callback(self, response: Message) -> Message:
        """
        Метод разбора ответа сервера.
        :param response: Сообщение от сервера
        :return:
        """
        if isinstance(response, str):
            print(response)
        if response.action == GET_CONTACTS:
            if response.quantity:
                print(f'\nСписок контактов ({response.quantity}).')
            if response.user:
                self.__repo.add_contact(response.user)
                print(f'{response.user or "Нет данных"}')
        elif response.action == SEND_MSG:
            if response.sender != response.destination:
                self.__repo.save_message(response.sender, "in", response.text)
                print(f'\nСообщение от {response.sender}: {response.text}')
        return response


class Gui(QObject):
    """Класс обработчика для графического режима."""

    new_message = pyqtSignal(Message)
    connection_lost = pyqtSignal()

    def __init__(self, parsed_args):
        QObject.__init__(self)
        self.__client = Client((parsed_args.addr, parsed_args.port))
        self.client_app = QApplication(sys.argv)
        self.__client.user_name, self.__client.password = \
            self.__validate_username(parsed_args.user, parsed_args.password)
        self.__client.keys = self.__client.create_keys()
        self.__repo = Repository(self.__client.user_name)
        self.__client.handler = self
        self.user_name = self.__client.user_name
        self.decrypter = PKCS1_OAEP.new(self.__client.keys)
        self.__listen_thread = Thread(target=self.run)
        self.__listen_thread.daemon = True

    def main(self):
        """
        Главный метод, запускающий необходимые компоненты.
        :return:
        """
        try:
            action = self.__client.connect()
            if not action:
                raise ConnectionResetError
            if not self.__client.auth(action):
                raise ServerError('Неправильный пароль.')
            self.__repo.clear_contacts()
            contacts = self.__client.load_contacts()
            if contacts:
                for message in contacts[1:]:
                    self.__repo.add_contact(message.user)
            self.__listen_thread.start()
            main_window = ClientMainWindow(self.__repo, self)
            main_window.make_connection(self)
            main_window.setWindowTitle(
                f'Чат Программа alpha release - {self.__client.user_name}')
            self.client_app.exec_()
        except (ConnectionResetError, ConnectionAbortedError):
            self.connection_lost.emit()
        except CUSTOM_EXCEPTIONS as ce:
            QMessageBox.warning(UserNameDialog(), "Warning", f'{ce}')
        finally:
            self.__listen_thread.is_alive = False
            self.__client.close()

    def run(self):
        """
        Метод запускающий получение и обработку сообщений.
        Работает в отдельном потоке.
        :return:
        """
        try:
            self.user_list_update()
            while True:
                messages = []
                try:
                    messages = receive(self.__client.sock,
                                       self.__client.logger)
                except socket.timeout:
                    pass
                while len(messages):
                    message = messages.pop()
                    checked_msg = self.__client.check_response(message)
                    self.receive_callback(checked_msg)
        except (ConnectionError, ConnectionAbortedError, ConnectionResetError):
            self.__listen_thread.is_alive = False
            self.connection_lost.emit()

    def __validate_username(self, user_name, password):
        """
        Метод проверки корректности введенных имени и пароля.
        :param user_name: Имя клиента
        :param password: Пароль клиента
        :return:
        """
        while True:
            if user_name == 'Гость' or not user_name or not password:
                start_dialog = UserNameDialog()
                self.client_app.exec_()
                # Если пользователь ввёл имя и нажал ОК,
                # то сохраняем ведённое и удаляем объект, инааче выходим
                if start_dialog.ok_pressed:
                    user_name = start_dialog.client_name.text()
                    password = start_dialog.client_passwd.text()
                    user_name = user_name.strip()
                    try:
                        if len(user_name) > 25:
                            raise UsernameToLongError
                    except UsernameToLongError as ce:
                        QMessageBox.warning(start_dialog, "Warning", f'{ce}')
                        user_name = ''
                        continue
                    del start_dialog
                else:
                    exit(0)
            else:
                break
        return user_name, password

    def user_list_update(self):
        """
        Метод, составляющий запрос на получение списка подключённых клиентов.
        :return:
        """
        self.__client.logger.debug(
            f'Запрос списка известных пользователей {self.__client.user_name}')
        data = {
            ACTION: GET_CONNECTED,
        }
        self.__client.send(Message(**data))

    def add_contact(self, contact):
        """
        Метод, составляющий запрос на добавление контакта.
        :param contact: Имя контакта
        :return:
        """
        self.__client.logger.debug(f'Создание контакта {contact}')
        data = {
            ACTION: ADD_CONTACT,
            USER: contact,
        }
        self.__client.send(Message(**data))

    # Функция удаления клиента на сервере
    def remove_contact(self, contact):
        """
        Метод, составляющий запрос на удаление контакта
        :param contact: Имя контакта
        :return:
        """
        self.__client.logger.debug(f'Удаление контакта {contact}')
        data = {
            ACTION: DEL_CONTACT,
            USER: contact,
        }
        self.__client.send(Message(**data))

    def send_message(self, to, message):
        """
        Метод, составляющий запрос на отправку сообщения контакту.
        :param to: Имя контакта
        :param message: Сообщение
        :return:
        """
        data = {ACTION: SEND_MSG, TO: to, TEXT: message}
        self.__client.send(Message(**data))

    def key_request(self, user_name):
        """
        Метод, составляющий запрос на получение открытого ключа контакта.
        :param user_name: Имя контакта
        :return:
        """
        data = {
            ACTION: PUBLIC_KEY_REQUEST,
            FROM: self.user_name,
            USER: user_name
        }
        with socket_lock:
            self.__client.send(Message(**data))
            responses = receive(self.__client.sock, self.__client.logger)
            if responses:
                response = responses[0]
                if response.response and response.text:
                    return response.text
            self.__client.logger.error(
                f'Не удалось получить ключ собеседника{user_name}.')

    def receive_callback(self, response: Message) -> Message:
        """
        Метод разбора ответа сервера.
        :param response: Сообщение от сервера.
        :return:
        """
        if isinstance(response, str):
            self.connection_lost.emit()
        if response.action == GET_CONNECTED:
            if response.user:
                self.__repo.add_client(response.user)
        if response.action == GET_CONTACTS:
            if response.quantity:
                pass
            if response.user:
                self.__repo.add_contact(response.user)
        elif response.action == SEND_MSG:
            if response.sender != response.destination:
                self.new_message.emit(response)
        return response
