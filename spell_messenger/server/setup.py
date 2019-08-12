import os
import sys

from setuptools import setup, find_packages

path = os.path.dirname(os.path.realpath(sys.argv[0]))
os.chdir(path)

setup(
    name="spell_messenger_server",
    version="4.0",
    description="Spell messenger - Server package",
    author="Antonina Kletskina",
    author_email="chepushilka@yandex.ru",
    url="https://github.com/SPELLGIRL/PyQT",
    packages=find_packages(exclude=[
        "*.tests", "*.tests.*", "tests.*", "tests"
    ]),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'],
    entry_points={
        'console_scripts':
        ['spell_messenger_server=spell_messenger_server:__main__']
    },
    zip_safe=False)
