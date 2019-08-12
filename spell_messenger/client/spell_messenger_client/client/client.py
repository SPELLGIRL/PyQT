"""
Функции ​клиента:​
- сформировать ​​presence-сообщение;
- отправить ​сообщение ​с​ерверу;
- получить ответ сервера;
- разобрать с​ообщение ​с​ервера;
- параметры командной строки скрипта client <addr> [<port>]:
- addr - ip-адрес сервера;
- port -​tcp-порт на сервере, по умолчанию 8000.
"""

import binascii
import hashlib
import hmac
import os
import socket
import time
from argparse import ArgumentParser

from Crypto.PublicKey import RSA

from jim.config import *
from jim.utils import Message, receive
from .decorators import Log
from .descriptors import Port
from .exceptions import ResponseCodeLenError, MandatoryKeyError, \
    ResponseCodeError, ServerError
from .log.config import client_logger
from .metaclasses import ClientVerifier
from .settings import DEFAULT_PORT, DEFAULT_IP

log_decorator = Log(client_logger)


class Client(metaclass=ClientVerifier):
    """Основной_класс_клиентского_модуля, отвечает_за_связь_с_сервером"""

    port = Port()

    def __init__(self, address):
        self.__logger = client_logger
        self.__addr, self.__port = address
        self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__user_name = None
        self.__password = None
        self.handler = None
        self.keys = None

        self.__sock.settimeout(5)
        super().__init__()

    @property
    def user_name(self):
        """Отображение имени пользователя"""
        return self.__user_name

    @user_name.setter
    def user_name(self, value):
        """Установка имени пользователя"""
        if self.__user_name is None:
            self.__user_name = value

    @property
    def password(self):
        """Отображение хэша пароля пользователя"""
        return self.__password

    @password.setter
    def password(self, value):
        """Установка хэша пароля из БД"""
        if self.__password is None:
            self.__password = value

    @property
    def logger(self):
        """логгер"""
        return self.__logger

    @property
    def sock(self):
        """Сокет пользователя"""
        return self.__sock

    def create_keys(self):
        """
        Метод загрузки ключей из файла или их создания, если файла нет.
        :return:
        """
        dir_path = os.path.dirname(os.path.abspath(__file__))
        keys_path = os.path.join(dir_path, 'keys')
        key_file = os.path.join(keys_path, f'{self.user_name}.key')
        if not os.path.exists(keys_path):
            os.mkdir(keys_path)
        if not os.path.exists(key_file):
            keys = RSA.generate(2048, os.urandom)
            with open(key_file, 'wb') as key:
                key.write(keys.export_key())
        else:
            with open(key_file, 'rb') as key:
                keys = RSA.import_key(key.read())
        keys.publickey().export_key()

        return keys

    def __check_presence(self):
        """Метод проверки соединения"""
        data = {ACTION: PRESENCE, FROM: self.__user_name}
        request = Message(data)
        self.send(request)
        messages = receive(self.__sock, self.__logger)
        return messages[0] if messages and messages[0].response == OK \
            else False

    def load_contacts(self):
        """Метод загрузки списка контактов"""
        data = {ACTION: GET_CONTACTS, FROM: self.user_name}
        request = Message(data)
        self.send(request)
        time.sleep(1)
        messages = receive(self.__sock, self.__logger)
        return messages or False

    @staticmethod
    def check_response(response):
        """Метод проверки корректности запроса"""
        if not isinstance(response, Message):
            raise TypeError
        if not getattr(response, RESPONSE):
            raise MandatoryKeyError(RESPONSE)
        code = getattr(response, RESPONSE)
        if len(str(code)) != 3:
            raise ResponseCodeLenError(code)
        if code not in RESPONSE_CODES:
            raise ResponseCodeError(code)
        return response

    @log_decorator
    def connect(self):
        """
        Метод отвечающий за установку соединения с сервером.
        :return:
        """
        result = False
        for i in range(5):
            try:
                self.__sock.connect((self.__addr, self.__port))
                response = self.__check_presence()
                if not response:
                    raise ConnectionRefusedError
                result = response
            except (ConnectionRefusedError, OSError) as e:
                print(e)
                info_msg = 'Сервер отклонил запрос на подключение.'
                print(info_msg)
                self.__logger.info(info_msg)
                continue
            else:
                break
            finally:
                time.sleep(1)
        return result

    def auth(self, response: Message):
        """Метод, отвечающий за авторизацию на сервере"""
        if response.action == REGISTER or response.action == AUTH:
            try:
                if response.action == REGISTER:
                    data = {
                        ACTION: REGISTER,
                        FROM: self.user_name,
                        TEXT: self.password
                    }
                    self.send(Message(**data))
                    response = receive(self.__sock, self.__logger)[0]

                # Получаем публичный ключ и декодируем его из байтов
                pubkey = self.keys.publickey().export_key().decode(
                    'ascii') if self.keys else None

                # Запускаем процедуру авторизации
                # Получаем хэш пароля
                passwd_bytes = self.password.encode('utf-8')
                salt = self.user_name.lower().encode('utf-8')
                passwd_hash = hashlib.pbkdf2_hmac('sha512', passwd_bytes, salt,
                                                  10000)
                passwd_hash_string = binascii.hexlify(passwd_hash)
                # Если сервер вернул ошибку, бросаем исключение.
                if response.response:
                    if response.response == FORBIDDEN:
                        raise ServerError(response.text)
                    elif response.response == OK:
                        # Если всё нормально,
                        # то продолжаем процедуру авторизации.
                        ans_data = response.text
                        hash_str = hmac.new(passwd_hash_string,
                                            ans_data.encode('utf-8'))
                        digest = hash_str.digest()
                        request_data = {
                            ACTION: AUTH,
                            FROM: self.user_name,
                            TEXT: binascii.b2a_base64(digest).decode('ascii'),
                            USER: pubkey
                        }
                        self.send(Message(**request_data))
                        responses = receive(self.__sock, self.__logger)
                        if responses and responses[0].response == OK:
                            info_msg = f'Клиент запущен ({self.user_name}).'
                            print(info_msg)
                            self.__logger.info(info_msg)
                            return True
                        else:
                            return False
            except OSError:
                raise ServerError('Сбой соединения в процессе авторизации.')

    def send(self, message: Message):
        """
        Метод, отправляющий сообщение серверу.
        :param message:
        :return:
        """
        self.__logger.info(f'Отправлено: {str(message)}.')
        return self.__sock.send(bytes(message))

    def close(self):
        """
        Метод закрытия соединения с сервером.
        :return:
        """
        self.__sock.close()


def parse_args(default_ip: str = DEFAULT_IP, default_port: int = DEFAULT_PORT):
    """
    Парсер аргументов коммандной строки.
    :param default_ip: IP адрес сервера
    :param default_port: Порт сервера
    :return:
    """
    parser = ArgumentParser(description='Запуск клиента.')
    parser.add_argument('addr',
                        nargs='?',
                        default=f'{default_ip}',
                        type=str,
                        help='IP адрес сервера')
    parser.add_argument('port',
                        nargs='?',
                        default=f'{default_port}',
                        type=int,
                        help='порт сервера')
    parser.add_argument('-u',
                        '--user',
                        default='Гость',
                        nargs='?',
                        help='Имя пользователя(по умолчанию Гость_****)')
    parser.add_argument('-p',
                        '--password',
                        nargs='?',
                        help='Пароль пользователя')
    parser.add_argument('-m',
                        '--mode',
                        default='gui',
                        type=str.lower,
                        nargs='?',
                        choices=['gui', 'console'],
                        help='Mode: GUI, Console (default console)')
    result = parser.parse_args()
    return result
