"""Модуль с моделями таблиц для БД"""

import datetime

from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    """
    Класс - таблица контактов.
    """
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Контакт {self.name}>'


class ConnectedUser(Base):
    """
    Класс - таблица подключённых пользователей.
    """
    __tablename__ = 'connecteduser'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Клиент {self.name}>'


class MessageHistory(Base):
    """
    Класс - таблица истории сообщений.
    """
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    contact = Column(String)
    direction = Column(String)
    message = Column(Text)
    time = Column(DateTime)

    def __init__(self, contact, direction, message):
        self.contact = contact
        self.direction = direction
        self.message = message
        self.time = datetime.datetime.now()

    def __repr__(self):
        return f'<Сообщение ' \
               f'{"отправлено" if self.direction == "in" else "получено от"}' \
               f' {self.contact}, {self.time}>'
