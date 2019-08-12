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


run()
