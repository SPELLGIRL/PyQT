import os
from db.models import Base, User, History, contact_table
from settings import DATABASE
from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import datetime


class Repository:
    def __init__(self, path=None, name=None):
        if not path:
            path = DATABASE
            if not os.path.exists(path):
                os.mkdir(path)
        if not name:
            name = "server.db"
        self.engine = create_engine(f'sqlite:///{os.path.join(path, name)}',
                                    echo=False,
                                    pool_recycle=7200,
                                    connect_args={'check_same_thread': False})

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)

        self.session = Session()
        self.new_connection = True

    def user_login(self, user_name, ip, key):
        user = self.get_user_by_name(user_name)
        if user:
            user.is_online = True
            user.last_login = datetime.datetime.now()
            if user.pubkey != key:
                user.pubkey = key
            self.add_login_history(user, ip)
            self.session.commit()
        else:
            raise ValueError('Пользователь не зарегистрирован.')

    def user_logout(self, user_name):
        user = self.get_user_by_name(user_name)
        if user:
            user.is_online = False
            self.session.commit()

    def add_user(self, user_name, password=None):
        user = self.get_user_by_name(user_name)
        if not user:
            user = User(user_name, password)
            self.session.add(user)
            self.session.commit()
        return user

    def remove_user(self, user_name):
        user = self.get_user_by_name(user_name)
        if user:
            self.session.query(User).filter_by(id=user.id).delete()
            self.session.query(History).filter_by(user_id=user.id).delete()
            contacts = self.session.query(contact_table).filter(
                or_(contact_table.c.user_id == user.id,
                    contact_table.c.contact_id == user.id))
            contacts.delete(synchronize_session=False)
            self.session.commit()

    def add_login_history(self, user, ip):
        history = History(user, ip)
        self.session.add(history)
        self.session.commit()

    def get_user_by_name(self, name):
        user = self.session.query(User).filter(User.name == name)
        return user.first() if user.count() else None

    def get_hash(self, user_name):
        user = self.get_user_by_name(user_name)
        return user.password if user else None

    def get_pubkey(self, user_name):
        user = self.get_user_by_name(user_name)
        return user.pubkey

    def users_list(self, active=None):
        query = self.session.query(User.name)
        if active is not None:
            query = query.filter(User.is_online == active)
        return [value for (value, ) in query.all()]

    def login_history(self, user_name=None):
        query = self.session.query(
            User.name, func.strftime('%Y-%m-%d %H:%M', History.time),
            History.ip).join(User)
        if user_name:
            query = query.filter(User.name == user_name)
        return [value for value in query.all()]

    def get_contact_list(self, user_name):
        user = self.get_user_by_name(user_name)
        return [contact.name for contact in user.contacts]

    def add_contact(self, user_name, contact_name):
        user = self.get_user_by_name(user_name)
        contact = self.get_user_by_name(contact_name)
        if contact:
            user.contacts.append(contact)
            self.session.add(user)
            self.session.commit()
        else:
            raise Exception

    def remove_contact(self, user_name, contact_name):
        user = self.get_user_by_name(user_name)
        contact = self.get_user_by_name(contact_name)
        if contact:
            user.contacts.remove(contact)
            self.session.add(user)
            self.session.commit()
        else:
            raise Exception

    def process_message(self, sender, recipient):
        sender = self.get_user_by_name(sender)
        recipient = self.get_user_by_name(recipient)
        if sender:
            sender.sent += 1
        if recipient:
            recipient.receive += 1
        self.session.commit()

    def message_history(self):
        query = self.session.query(User.name, User.last_login, User.sent,
                                   User.receive)
        return query.all()


if __name__ == '__main__':
    test_db = Repository()
    test_db.user_login('client_1', '192.168.1.4')
    test_db.user_login('client_2', '192.168.1.5')
    test_db.add_contact('client_1', 'client_2')
    print(test_db.users_list(active=True))
    test_db.user_logout('client_1')
    print(test_db.users_list(active=True))
    print(test_db.login_history('client_1'))
    print(test_db.users_list())
    print(test_db.get_contact_list('client_1'))
    print(test_db.get_contact_list('client_2'))
