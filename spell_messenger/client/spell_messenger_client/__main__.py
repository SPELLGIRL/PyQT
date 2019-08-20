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

from main import run

run()
