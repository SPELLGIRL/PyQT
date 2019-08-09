import datetime
from sqlalchemy import Column, Table, String, Integer, Boolean, ForeignKey, \
    DateTime, Text
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

contact_table = Table(
    'contact', Base.metadata,
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('contact_id', Integer, ForeignKey('user.id'))
)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    password = Column(String)
    pubkey = Column(Text)
    last_login = Column(DateTime)
    is_online = Column(Boolean)
    sent = Column(Integer, default=0)
    receive = Column(Integer, default=0)
    history = relationship('History', back_populates='user')
    contacts = relationship('User', secondary=contact_table,
                            backref='owner',
                            primaryjoin=id == contact_table.c.user_id,
                            secondaryjoin=id == contact_table.c.contact_id,
                            )

    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.pubkey = None

    def __repr__(self):
        return f'<Клиент {self.name}>'


class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    time = Column(DateTime)
    ip = Column(String)
    user = relationship('User', back_populates='history')

    def __init__(self, user, ip):
        self.ip = ip
        self.user = user
        self.time = datetime.datetime.now()

    def __repr__(self):
        return f'<История {self.user.name}, {self.time}, {self.ip}>'
