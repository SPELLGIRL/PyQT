from handlers import Console, Gui
from client import Client, parse_args


def run():
    args = parse_args()
    client = Client((args.addr, args.port), args.user)
    if args.mode == 'gui':
        handler = Gui(client)
    else:
        handler = Console(client)
    if client.connect():
        handler.main()


run()
