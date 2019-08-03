import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<Контакт {self.name}>'


class MessageHistory(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    sender = Column(String)
    to = Column(String)
    message = Column(Text)
    time = Column(DateTime)

    def __init__(self, sender, to, message):
        self.sender = sender
        self.to = to
        self.message = message
        self.time = datetime.datetime.now()

    def __repr__(self):
        return f'<История {self.sender} to {self.to}, {self.time}>'
