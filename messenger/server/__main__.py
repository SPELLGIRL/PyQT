from s_handlers import Console, Gui
from server import parse_args


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


run()
