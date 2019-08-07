"""
Функции ​​сервера:​
- принимает ​с​ообщение ​к​лиента;
- формирует ​​ответ ​к​лиенту;
- отправляет ​​ответ ​к​лиенту;
- имеет ​​параметры ​к​омандной ​с​троки:
- -p ​​<port> ​-​ ​​TCP-порт ​​для ​​работы ​(​по ​у​молчанию ​​использует ​​порт ​​8000);
- -a ​​<addr> ​-​ ​I​P-адрес ​​для ​​прослушивания ​(​по ​у​молчанию ​с​лушает ​​все ​​доступные ​​адреса).
"""
import select
from argparse import ArgumentParser
from settings import DEFAULT_PORT, DEFAULT_IP, MAX_CONNECTIONS, TIMEOUT
import socket
import threading
import hmac
import hashlib
import binascii
import os
from jim.utils import Message, receive, accepted, success, error, forbidden
from jim.config import *
from log.config import server_logger
from decorators import Log, login_required
from metaclasses import ServerVerifier
from descriptors import Port

log_decorator = Log(server_logger)
conflag_lock = threading.Lock()


class Dispatcher:
    __slots__ = (
        'sock', 'user_name', '__logger', '__repo', '__in', '__out', 'status',
        'random_str', 'ip'
    )

    def __init__(self, sock, ip, repository):
        self.sock = sock
        self.user_name = None
        self.ip = ip
        self.__repo = repository
        self.__logger = server_logger
        self.__in = []
        self.__out = []
        # Набор байтов в hex представлении
        self.random_str = binascii.hexlify(os.urandom(64))
        self.status = False
        self.receive()
        self.process()
        self.release()

    def create_digest(self, password):
        # Создаём хэш пароля и связки с рандомной строкой, сохраняем серверную версию ключа
        hash_str = hmac.new(password, self.random_str)
        return hash_str.digest()

    def auth(self, request):
        def auth_request():
            auth_data = {
                ACTION: AUTH,
                TEXT: self.random_str.decode('ascii')
            }
            return auth_data

        if request.action == PRESENCE:
            self.user_name = request.sender
            if request.sender in self.__repo.users_list(active=True):
                data = {
                    TEXT: 'Имя пользователя уже занято.'
                }
                return forbidden(**data)
            elif not self.__repo.get_user_by_name(request.sender):
                data = {
                    ACTION: REGISTER,
                }
            else:
                data = auth_request()
            self.status = True
            return success(**data)
        elif request.action == REGISTER:
            passwd_bytes = request.text.encode('utf-8')
            salt = request.sender.lower().encode('utf-8')
            passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt, 10000)
            self.__repo.add_user(request.sender, binascii.hexlify(passwd_hash))
            data = auth_request()
            return success(**data)
        elif request.action == AUTH:
            client_digest = binascii.a2b_base64(request.text)
            # Если ответ клиента корректный, то сохраняем его в список пользователей.
            digest = self.create_digest(self.__repo.get_hash(request.sender))
            if hmac.compare_digest(digest, client_digest):
                # добавляем пользователя в список активных и если у него изменился открытый ключ
                # сохраняем новый
                self.__repo.user_login(self.user_name, self.ip)
                self.__repo.new_connection = True
                return success()
            else:
                self.status = False
                return forbidden(text='Неверный пароль.')

    def receive(self):
        requests = receive(self.sock, self.__logger)
        if not requests:
            raise Exception
        self.__in.extend(requests)

    def process(self):
        while len(self.__in):
            request = self.__in.pop()
            if not request.sender:
                request.sender = self.user_name
            response = self.run_action(request)
            if isinstance(response, Message):
                self.__out.append(response)
            else:
                self.__out.extend(response)

    @login_required
    def run_action(self, request):
        if request.action in (PRESENCE, REGISTER, AUTH):
            return self.auth(request)
        elif request.action == SEND_MSG:
            contacts = request.destination.replace(' ', '').split(',')
            if len(contacts) == 1 and (not contacts[0] or contacts[0] == '*'):
                contacts = self.__repo.get_contact_list(request.sender)
            responses = []
            for contact in contacts:
                data = {
                    ACTION: SEND_MSG,
                    TEXT: request.text,
                    TO: contact,
                    FROM: request.sender,
                }
                self.__repo.process_message(request.sender, contact)
                responses.append(success(**data))
            return responses
        elif request.action == GET_CONTACTS:
            names = self.__repo.get_contact_list(request.sender)
            count = len(names)
            data = {
                ACTION: GET_CONTACTS,
                QUANTITY: count,
            }
            responses = [accepted(**data)]
            for contact in names:
                data = {
                    ACTION: GET_CONTACTS,
                    USER: contact,
                }
                responses.append(accepted(**data))
            return responses
        elif request.action == GET_CONNECTED:
            names = self.__repo.users_list(active=True)
            responses = []
            for contact in names:
                data = {
                    ACTION: GET_CONNECTED,
                    USER: contact,
                }
                responses.append(accepted(**data))
            return responses
        elif request.action == ADD_CONTACT:
            if request.sender == request.user:
                return error('Нельзя добавить себя')
            try:
                self.__repo.add_contact(request.sender, request.user)
                return success()
            except Exception:
                return error('Контакта не существует')
        elif request.action == DEL_CONTACT:
            try:
                self.__repo.remove_contact(request.sender, request.user)
                return success()
            except Exception:
                return error('Контакта не существует')
        elif request.action == ERROR:
            return error('Ошибка действия')
        else:
            return error('Действие недоступно')

    def release(self, names=None):
        while len(self.__out):
            response = self.__out.pop(0)
            if response.destination:
                if response.destination in names:
                    client_socket = names[response.destination]
                    client_socket.send(bytes(response))
            else:
                self.sock.send(bytes(response))
            self.__logger.info(f'Отправлено: {str(response)}.')


class Server(threading.Thread, metaclass=ServerVerifier):
    __port = Port()

    def __init__(self, address, database):
        self.__logger = server_logger
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__repo = database
        self.__client_sockets = []
        self.__socket_dispatcher = {}
        self.__name_socket = {}
        self.__in = []
        self.__out = []
        self.__addr, self.__port = address
        self.handler = None

        self.__sock.bind((self.__addr, self.__port))
        self.__sock.listen(MAX_CONNECTIONS)
        self.__sock.settimeout(TIMEOUT)

        info_msg = f'Сервер запущен ({address[0] or "*"}:{address[1]}).'
        print(info_msg)
        self.__logger.info(info_msg)
        super().__init__()

    def run(self):
        try:
            for user in self.__repo.users_list():
                self.__repo.user_logout(user)
            while True:
                try:
                    client, address = self.__sock.accept()
                    dispatcher = Dispatcher(client, address[0], self.__repo)
                except OSError:
                    pass
                else:
                    if dispatcher.status:
                        self.__client_sockets.append(client)
                        self.__socket_dispatcher[client] = dispatcher
                        self.__name_socket[dispatcher.user_name] = client
                        info_msg = f'User "{self.__user_name(client)}" ' \
                                   f'from {address} connected. ' \
                                   f'Current {len(self.__client_sockets)}.'
                        self.__logger.info(info_msg)
                finally:
                    r = []
                    w = []
                    try:
                        r, w, e = select.select(self.__client_sockets,
                                                self.__client_sockets,
                                                [], 0)
                    except Exception:
                        pass
                    self.__input(r)
                    self.__process()
                    self.__output(w)

        except KeyboardInterrupt:
            info_msg = 'Сервер остановлен по команде пользователя.'
            self.__logger.info(info_msg)
            print(info_msg)

    def __input(self, clients):
        for sock in clients:
            try:
                dispatcher = self.__socket_dispatcher[sock]
                dispatcher.receive()
                self.__in.append(dispatcher)
            except Exception:
                self.__remove_client(sock)

    def __process(self):
        while len(self.__in):
            dispatcher = self.__in.pop()
            dispatcher.process()
            self.__out.append(dispatcher)

    def __output(self, clients):
        while len(self.__out):
            dispatcher = self.__out.pop()
            try:
                if dispatcher.sock in clients:
                    dispatcher.release(self.__name_socket)
                else:
                    raise ConnectionRefusedError
            except Exception:
                self.__remove_client(dispatcher.sock)

    def __remove_client(self, client):
        self.__client_sockets.remove(client)
        name = self.__socket_dispatcher.pop(client)
        self.__name_socket.pop(name.user_name)
        self.__repo.user_logout(name.user_name)
        self.__repo.new_connection = True
        info_msg = f'Клиент {name.user_name} отключён. ' \
                   f'Текущее количество клиентов: {len(self.__client_sockets)}.'
        self.__logger.info(info_msg)
        client.close()

    def __user_name(self, client):
        return self.__socket_dispatcher[client].user_name


def parse_args(default_ip=DEFAULT_IP, default_port=DEFAULT_PORT):
    parser = ArgumentParser(description='Запуск сервера.')
    parser.add_argument(
        '-a', nargs='?', default=f'{default_ip}', type=str,
        help='ip адрес интерфейса (по умолчанию любой)'
    )
    parser.add_argument(
        '-p', nargs='?', default=default_port, type=int,
        help='порт сервера в диапазоне от 1024 до 65535'
    )
    parser.add_argument(
        '-m',
        default='console',
        type=str.lower,
        nargs='?',
        choices=['gui', 'console'],
        help='Mode: GUI, Console (default console)')
    result = parser.parse_args()
    # if result.p not in range(1024, 65535):
    #     parser.error(
    #         f'argument -p: invalid choice: {result.p} (choose from 1024-65535)'
    #     )
    return result
