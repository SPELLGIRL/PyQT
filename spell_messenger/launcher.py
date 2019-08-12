import os
import subprocess
import time
from argparse import ArgumentParser


class Launcher:
    """
    Основной класс лаунчера.
    """
    def __init__(self, num, start, sm, cm):
        self.__server = None
        self.__clients = []
        self.__actions = {
            'q': 'Выход',
            's': 'Запустить сервер и клиенты (s <кол-во>)',
            'x': 'Закрыть все окна',
            'h': 'Справка',
        }
        self.__num = num
        self.__server_mode = sm
        self.__client_mode = cm
        if start == 'y':
            self.run()

    @property
    def __help_info(self) -> str:
        """
        Вывод списка возможных действий.
        :return:
        """
        return '\n'.join(
            [f'{key} - {action}' for key, action in self.__actions.items()])

    def main(self):
        """
        Метод, описывающий команды управления запуском.
        :return:
        """
        print(self.__help_info)
        while True:
            action = input('Выберите действие: ')
            if action == 'q':
                break
            elif action.startswith('s'):
                command = f'{action} {self.__num}'.split(' ')
                if command[0] == 's' and len(command) <= 3:
                    try:
                        self.__num = int(command[1])
                    except ValueError:
                        continue
                    self.run()
            elif action == 'x':
                self.close()
            elif action == 'h':
                print(self.__help_info)

    def run(self):
        """
        Основной метод, запускающий окна программ.
        :return:
        """
        self.close()
        time.sleep(1)
        print('Запускаем сервер...')
        if self.__server_mode == 'gui':
            self.__server = subprocess.Popen(
                'python server/spell_messenger_server -m gui')
        else:
            self.__server = subprocess.Popen(
                'python server/spell_messenger_server',
                creationflags=subprocess.CREATE_NEW_CONSOLE)
        time.sleep(2)
        print('Запускаем клиентов...')
        for i in range(self.__num):
            if self.__client_mode == 'gui':
                self.__clients.append(
                    subprocess.Popen(
                        f'python client/spell_messenger_client -u test{i} -p test{i} -m gui'
                    ))
            else:
                self.__clients.append(
                    subprocess.Popen(
                        f'python client/spell_messenger_client -u test{i} -p test{i}',
                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        time.sleep(10)

    def close(self):
        """
        Метод, закрывающий окна программ.
        :return:
        """
        while self.__clients:
            process = self.__clients.pop()
            process.kill()
        if self.__server:
            self.__server.kill()


def parse_args():
    """
    Парсер аргументов коммандной строки.
    :return:
    """
    parser = ArgumentParser(description='Запуск сервера.')
    parser.add_argument('-n',
                        '--num',
                        nargs='?',
                        default=2,
                        type=int,
                        choices=range(1, 11),
                        help='количество клиентов)')
    parser.add_argument('-r',
                        '--run',
                        nargs='?',
                        default='n',
                        choices=('y', 'n'),
                        type=str.lower,
                        help='Моментальный запуск y/n')
    parser.add_argument('-sm',
                        nargs='?',
                        default='gui',
                        choices=('console', 'gui'),
                        type=str.lower,
                        help='Режим сервера (Console/GUI)')
    parser.add_argument('-cm',
                        nargs='?',
                        default='gui',
                        choices=('console', 'gui'),
                        type=str.lower,
                        help='Режим клиента (Console/GUI)')
    return parser.parse_args()


def run():
    """
    Функция запуска.
    :return:
    """
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    args = parse_args()
    launcher = Launcher(args.num, args.run, args.sm, args.cm)
    launcher.main()


if __name__ == '__main__':
    run()
