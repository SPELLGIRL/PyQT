from handlers import Console, Gui
from client import parse_args


def run():
    args = parse_args()
    if args.mode == 'gui':
        handler = Gui(args)
    else:
        handler = Console(args)
    handler.main()


run()
