from cx_Freeze import setup, Executable

build_exe_options = {'packages': ['server', 'jim']}

setup(name='spell_messenger_server',
      version='0.1',
      description='Spell messenger - Server',
      options={'build_exe': build_exe_options},
      executables=[
          Executable('__main__.py',
                     base='Win32GUI',
                     targetName='spell_server.exe')
      ])
