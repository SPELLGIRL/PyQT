import os
import sys

from cx_Freeze import setup, Executable

path = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])),
                    'spell_messenger_server')
os.chdir(path)
sys.path.insert(0, path)

build_exe_options = {'packages': ['server', 'jim']}

setup(name='spell_messenger_server',
      version='4.0',
      description='Spell messenger - Server',
      options={'build_exe': build_exe_options},
      executables=[
          Executable('__main__.py',
                     base='Win32GUI',
                     targetName='spell_server.exe')
      ])
