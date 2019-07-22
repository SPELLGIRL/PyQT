import subprocess
from argparse import ArgumentParser


class Launcher:
    def __init__(self, num, start):
        self.__server = None
        self.__clients = []
        self.__actions = {
            'q': 'Выход',
            's': 'Запустить сервер и клиенты (s <кол-во>)',
            'x': 'Закрыть все окна',
            'h': 'Справка',
        }
        self.__num = num
        if start == 'y':
            self.run()

    @property
    def __help_info(self):
        return '\n'.join(
            [f'{key} - {action}' for key, action in self.__actions.items()])

    def main(self):
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
        self.close()
        self.__server = subprocess.Popen('python server',
                                         creationflags=subprocess.CREATE_NEW_CONSOLE)
        for i in range(self.__num):
            self.__clients.append(
                subprocess.Popen(f'python client -u test{i}',
                                 creationflags=subprocess.CREATE_NEW_CONSOLE))

    def close(self):
        while self.__clients:
            process = self.__clients.pop()
            process.kill()
        if self.__server:
            self.__server.kill()


def parse_args():
    parser = ArgumentParser(description='Запуск сервера.')
    parser.add_argument(
        '-n', '--num', nargs='?', default=2, type=int, choices=range(1, 11),
        help='количество клиентов)'
    )
    parser.add_argument(
        '-r', '--run', nargs='?', default='n', choices=('y', 'n'),
        type=str.lower, help='Моментальный запуск y/n'
    )
    return parser.parse_args()


def run():
    args = parse_args()
    launcher = Launcher(args.num, args.run)
    launcher.main()


if __name__ == '__main__':
    run()
