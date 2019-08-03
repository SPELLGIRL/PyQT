from handlers import Console, Gui
from server import parse_args


def run():
    args = parse_args()
    if args.m == 'gui':
        handler = Gui()
    else:
        handler = Console(args)
    handler.main()


run()
