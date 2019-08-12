from setuptools import setup, find_packages

setup(
    name="spell_messenger_client",
    version="0.1",
    description="Spell messenger - Client package",
    author="Antonina Kletskina",
    author_email="chepushilka@yandex.ru",
    url="https://github.com/SPELLGIRL/PyQT",
    packages=find_packages(exclude=[
        "*.tests", "*.tests.*", "tests.*", "tests", "*.server", "*.server.*",
        "server", "server"
    ]),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'])
