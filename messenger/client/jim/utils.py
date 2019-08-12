"""Утилиты для работы с протоколом."""

import json
import time

from client.settings import ENCODING, MAX_PACKAGE_LENGTH
from .config import *


class Message:
    """
    Класс сообщения.

    """
    def __init__(self, data=None, **kwargs):
        if data:
            if isinstance(data, dict):
                data.update(kwargs)
            kwargs = data
        self.__raw = kwargs
        if not self.__raw.get(TIME):
            self.__raw[TIME] = time.time()

    def __bytes__(self):
        return f'{json.dumps(self.__raw)}{DELIMITER}'.encode(ENCODING)

    def __str__(self):
        return str(self.__raw)

    @property
    def raw(self) -> dict:
        """Словарь с данными"""
        return self.__raw

    @property
    def action(self) -> str:
        """Действие"""
        return self.__raw.get(ACTION)

    @property
    def response(self) -> int:
        """Код ответа"""
        return self.__raw.get(RESPONSE)

    @property
    def time(self) -> str:
        """Время составления"""
        struct_time = time.localtime(self.__raw.get(TIME))
        return time.strftime(DATE_FORMAT, struct_time) if struct_time else None

    @property
    def quantity(self):
        """Информация о количестве"""
        return self.__raw.get(QUANTITY)

    @property
    def user(self) -> str:
        """Информация о клиенте"""
        return self.__raw.get(USER)

    @property
    def destination(self) -> str:
        """Получатель"""
        return self.__raw.get(TO)

    @destination.setter
    def destination(self, value: str):
        """Установка получателя"""
        self.__raw[TO] = value

    @property
    def sender(self) -> str:
        """Отправитель"""
        return self.__raw.get(FROM)

    @sender.setter
    def sender(self, value):
        """Установка отправителя"""
        self.__raw[FROM] = value

    @property
    def error(self):
        return self.__raw.get(ERROR)

    @property
    def text(self) -> str:
        """Переданный текст"""
        return self.__raw.get(TEXT)


def error(text, **kwargs) -> Message:
    """
    Функция составляет сообщение об ошибке на основе переданных аргументов.

    """
    data = {
        RESPONSE: WRONG_REQUEST,
        ACTION: ERROR,
        TEXT: text,
    }
    return Message(data, **kwargs)


def success(**kwargs) -> Message:
    """
    Функция составляет сообщение об успехе на основе переданных аргументов.

    """
    data = {
        RESPONSE: OK,
    }
    return Message(data, **kwargs)


def accepted(**kwargs) -> Message:
    """
    Функция составляет сообщение о разрешении действия
    на основе переданных аргументов.

    """
    data = {RESPONSE: ACCEPTED}
    return Message(data, **kwargs)


def forbidden(**kwargs) -> Message:
    """
    Функция составляет сообщение о запрете действия
    на основе переданных аргументов.

    """
    data = {RESPONSE: FORBIDDEN}
    return Message(data, **kwargs)


def receive(sock, logger) -> list:
    """
    Функция приёма сообщений от удалённых компьютеров.
    Принимает сообщения JSON, декодирует полученное сообщение
    и проверяет что получен словарь.
    :param sock: сокет для передачи данных.
    :param logger: логгер
    :return: список сообщений

    """
    requests = []
    try:
        bytes_response = sock.recv(MAX_PACKAGE_LENGTH)
    except UnicodeDecodeError:
        text = 'Соединение разорвано'
        logger.info(text)
        requests.append(error(text))
        return []
    try:
        raw_string = bytes_response.decode(ENCODING)
    except UnicodeDecodeError as e:
        text = f'Ошибка кодировки: {e}'
        logger.info(text)
        requests.append(error(text))
    else:
        try:
            raw_strings = list(filter(None, raw_string.split(DELIMITER)))
            messages = list(map(json.loads, raw_strings))
        except (ValueError, json.decoder.JSONDecodeError):
            text = f'Неверный формат json "{raw_string}"'
            logger.info(text)
            requests.append(error(text))
        else:
            if messages:
                logger.info(f'Получены сообщения: {list(messages)}')
                requests.extend([Message(**message) for message in messages])
    return requests
