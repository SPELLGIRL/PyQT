import os
import re
from argparse import ArgumentParser


def parse_args():
    """
    Парсер аргументов коммандной строки.
    :return:
    """
    parser = ArgumentParser(description='Запуск сервера.')
    parser.add_argument('-m',
                        '--mode',
                        nargs='?',
                        default='all',
                        type=str,
                        choices=('all', 'client', 'server'),
                        help='Режим очистки)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    pattern = r'^(((\S*)\.log\.((19|[2-9]\d)\d{2}))\-(0[13578]|1[02])\-(0[1-9]|[12]\d|3[01])|((\S*)\.log\.((19|[2-9]\d)\d{2}))\-(0[13456789]|1[012])\-(0[1-9]|[12]\d|30)|((\S*)\.log\.((19|[2-9]\d)\d{2}))\-02\-(0[1-9]|1\d|2[0-8])|((\S*)\.log\.((1[6-9]|[2-9]\d)(0[48]|[2468][048]|[13579][26])|((16|[2468][048]|[3579][26])00)))\-02\-29)$'
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    clear_dir = {
        'console': os.path.join(cur_dir, 'console'),
        'server': os.path.join(cur_dir, 'server'),
        'all': cur_dir
    }
    for root, dirs, files in os.walk(clear_dir[args.mode]):
        for file in files:
            if file.endswith(
                ('.log', '.db', '.key')
            ) or re.fullmatch(pattern, file):
                print(os.path.join(root, file))
                os.remove(os.path.join(root, file))
