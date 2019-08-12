import os
import sys

path = os.path.realpath(sys.argv[0])
if path.endswith(('exe')):
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if path.endswith('Scripts'):
        path = os.path.join(os.path.dirname(path),
                            'Lib/site-packages/spell_messenger_server')
else:
    path = os.path.dirname(os.path.realpath(__file__))
    if not path.endswith('spell_messenger_server'):
        path = os.path.join(path, 'spell_messenger_server')
sys.path.insert(0, path)

from server.handlers import Console, Gui
from server.server import parse_args


def run():
    """
    Функция для определения режима запуска приложения
    :return:
    """
    args = parse_args()
    if args.m == 'gui':
        handler = Gui()
    else:
        handler = Console()
    handler.main()


if __name__ == '__main__':
    run()
