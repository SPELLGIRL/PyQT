from db.models import Base, Contact, MessageHistory
from settings import DATABASE
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
import datetime


class Repository:
    def __init__(self, name):
        self.engine = create_engine(DATABASE + f'_{name}.db', echo=False,
                                    pool_recycle=7200,
                                    connect_args={'check_same_thread': False})

        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)

        self.session = Session()

    def add_contact(self, user_name):
        if not self.session.query(exists().where(Contact.name == user_name)).scalar():
            contact = Contact(user_name)
            self.session.add(contact)
            self.session.commit()
            return contact

    def del_contact(self, contact):
        self.session.query(Contact).filter_by(name=contact).delete()
        self.session.commit()

    def clear_contacts(self):
        self.session.query(Contact).delete()
        self.session.commit()

    def save_message(self, sender, to, message):
        message_row = MessageHistory(sender, to, message)
        self.session.add(message_row)
        self.session.commit()

    def get_history(self, sender=None, to=None):
        query = self.session.query(MessageHistory)
        if sender:
            query = query.filter_by(sender=sender)
        if to:
            query = query.filter_by(to=to)
        return [(history_row.sender, history_row.to, history_row.message,
                 history_row.time)
                for history_row in query.all()]

    def get_contacts(self):
        query = self.session.query(Contact.name).all()
        return [value for (value,) in query]


if __name__ == '__main__':
    test_db = Repository('test1')
    for i in ['test3', 'test4', 'test5']:
        test_db.add_contact(i)
    test_db.add_contact('test4')
    test_db.save_message('test1', 'test2', f'Привет! я тестовое сообщение от {datetime.datetime.now()}!')
    test_db.save_message('test2', 'test1', f'Привет! я другое тестовое сообщение от {datetime.datetime.now()}!')
    print(test_db.get_contacts())
    print(test_db.get_history('test2'))
    print(test_db.get_history(to='test2'))
    print(test_db.get_history('test3'))
    test_db.del_contact('test4')
    print(test_db.get_contacts())
