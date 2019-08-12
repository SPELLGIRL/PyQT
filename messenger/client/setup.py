from cx_Freeze import setup, Executable

build_exe_options = {'packages': ['client', 'jim']}

setup(name='spell_messenger_client',
      version='0.1',
      description='Spell messenger - Client',
      options={'build_exe': build_exe_options},
      executables=[
          Executable('__main__.py',
                     base='Win32GUI',
                     targetName='spell_client.exe')
      ])
