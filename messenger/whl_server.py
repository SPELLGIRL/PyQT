from setuptools import setup, find_packages

setup(
    name="spell_messenger_server",
    version="0.1",
    description="Spell messenger - Server package",
    author="Antonina Kletskina",
    author_email="chepushilka@yandex.ru",
    url="http://www.blog.pythonlibrary.org",
    packages=find_packages(exclude=[
        "*.tests", "*.tests.*", "tests.*", "tests", "*.client", "*.client.*",
        "client", "client"
    ]),
    install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex'])
