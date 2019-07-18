import socket
from threading import Thread
from random import randint
from jim.utils import Message, receive
from jim.config import *
from exceptions import *
from client import log_decorator


class Console:
    __slots__ = ('__client', '__actions', '__listen_thread')

    def __init__(self, client, user_name):
        self.__client = client
        self.__client.user_name = self.__validate_username(user_name)
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
                'params': (TO, TEXT,)
            },
            {
                ACTION: GET_CONTACTS,
                'name': 'Запросить список контактов',
            },
            {
                ACTION: 'help',
                'name': 'Справка',
            },
        )

    @staticmethod
    def __validate_username(user_name):
        while True:
            if user_name == 'Гость' or not user_name:
                user_name = input('Введите своё имя: ') or \
                            f'Гость_{randint(1, 9999)}'
                try:
                    if len(user_name) > 25:
                        raise UsernameToLongError
                    break
                except UsernameToLongError as ce:
                    print(ce)
            else:
                break
        return user_name

    @log_decorator
    def interact(self):
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
                if start[ACTION] == 'help':
                    print(self.__help_info)
                    continue
                params = {ACTION: start[ACTION]}
                if 'params' in start:
                    for param in start['params']:
                        p = str(input(f'Выберите параметр "{param}": '))
                        params[param] = p
                break
            except ValueError:
                print('Действие не распознано, попробуйте еще раз...')
                pass
        return Message(**params)

    @property
    def __help_info(self):
        return '\n'.join([f'{key}. {action["name"]}' for key, action in
                          enumerate(self.__actions, 0)])

    def main(self):
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
        try:
            while True:
                messages = []
                try:
                    messages = receive(self.__client.sock, self.__client.logger)
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

    @staticmethod
    def receive_callback(response):
        if isinstance(response, str):
            print(response)
        if response.action == GET_CONTACTS:
            if response.quantity:
                print(f'\nСписок контактов (подключено {response.quantity}).')
            if response.user:
                print(f'{response.user or "Нет данных"}')
        elif response.action == SEND_MSG:
            if response.sender != response.destination:
                print(f'\nСообщение от {response.sender}: {response.text}')
        return response


class Gui:
    __slots__ = ('__client',)

    def __init__(self, client):
        self.__client = client
        pass

    def run(self):
        pass
