"""
Функции ​к​лиента:​
- сформировать ​​presence-сообщение;
- отправить ​с​ообщение ​с​ерверу;
- получить ​​ответ ​с​ервера;
- разобрать ​с​ообщение ​с​ервера;
- параметры ​к​омандной ​с​троки ​с​крипта ​c​lient ​​<addr> ​[​<port>]:
- addr ​-​ ​i​p-адрес ​с​ервера;
- port ​-​ ​t​cp-порт ​​на ​с​ервере, ​​по ​у​молчанию ​​8000.
"""


from socket import socket, AF_INET, SOCK_STREAM
from argparse import ArgumentParser
from settings import DEFAULT_PORT, DEFAULT_IP
from exceptions import ResponseCodeLenError, MandatoryKeyError, \
    ResponseCodeError
from jim.config import *
from jim.utils import Message, receive
from decorators import Log
from log.config import client_logger

log_decorator = Log(client_logger)


class Client:
    __slots__ = ('__logger', '__host', '__sock', '__user_name')

    def __init__(self, address):
        self.__logger = client_logger
        self.__host = address
        self.__sock = socket(AF_INET, SOCK_STREAM)
        self.__user_name = None

        self.__sock.settimeout(1)

    @property
    def user_name(self):
        return self.__user_name

    @user_name.setter
    def user_name(self, value):
        if self.__user_name is None:
            self.__user_name = value

    @property
    def logger(self):
        return self.__logger

    @property
    def sock(self):
        return self.__sock

    def __check_presence(self):
        data = {
            ACTION: PRESENCE,
            FROM: self.__user_name
        }
        request = Message(data)
        self.send(request)
        messages = receive(self.__sock, self.__logger)
        return messages[0].response == OK if messages else False

    @staticmethod
    def check_response(response):
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
        result = False
        try:
            self.__sock.connect(self.__host)
            if not self.__check_presence():
                raise ConnectionRefusedError
            info_msg = f'Клиент запущен ({self.user_name}).'
            result = True
        except (ConnectionRefusedError, OSError):
            info_msg = 'Сервер отклонил запрос на подключение.'
        print(info_msg)
        self.__logger.info(info_msg)
        return result

    def send(self, message):
        self.__logger.info(f'Отправлено: {str(message)}.')
        return self.__sock.send(bytes(message))

    def close(self):
        self.__sock.close()


def parse_args():
    parser = ArgumentParser(description='Запуск клиента.')
    parser.add_argument(
        'addr', nargs='?', default=f'{DEFAULT_IP}', type=str,
        help='IP адрес сервера'
    )
    parser.add_argument(
        'port', nargs='?', default=f'{DEFAULT_PORT}', type=int,
        help='порт сервера'
    )
    parser.add_argument(
        '-u',
        '--user',
        default='Гость',
        nargs='?',
        help='Имя пользователя(по умолчанию Гость_****)')
    parser.add_argument(
        '-m',
        '--mode',
        default='console',
        type=str.lower,
        nargs='?',
        choices=['gui', 'console'],
        help='Mode: GUI, Console (default console)')
    result = parser.parse_args()
    if result.port not in range(1024, 65535):
        parser.error(
            f'argument port: invalid choice: {result.port} (choose from 1024-65535)'
        )
    return result
