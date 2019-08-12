import os
import sys

path = os.path.realpath(sys.argv[0])
if path.endswith(('exe')):
    path = os.path.dirname(os.path.realpath(sys.argv[0]))
    if path.endswith('Scripts'):
        path = os.path.join(os.path.dirname(path),
                            'Lib/site-packages/spell_messenger_client')
else:
    path = os.path.dirname(os.path.realpath(__file__))
    if not path.endswith('spell_messenger_client'):
        path = os.path.join(path, 'spell_messenger_client')
sys.path.insert(0, path)

from client.client import parse_args
from client.handlers import Console, Gui


def run():
    """
    Функция для определения режима запуска приложения
    :return:
    """
    args = parse_args()
    if args.mode == 'gui':
        handler = Gui(args)
    else:
        handler = Console(args)
    handler.main()

if __name__=='__main__':
    run()
