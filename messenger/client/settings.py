import os

# Порт поумолчанию для сетевого ваимодействия
DEFAULT_PORT = 8000
# IP адрес по умолчанию для подключения к серверу
DEFAULT_IP = '127.0.0.1'
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'
# База данных
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db/storage")