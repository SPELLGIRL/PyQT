import os

# Порт поумолчанию для сетевого ваимодействия
DEFAULT_PORT = 8000
# IP адрес по умолчанию для подключения клиента
DEFAULT_IP = ''
# Максимальная очередь подключений
MAX_CONNECTIONS = 5
# Максимальная длинна сообщения в байтах
MAX_PACKAGE_LENGTH = 1024
# Кодировка проекта
ENCODING = 'utf-8'
# Время ожидания
TIMEOUT = 0.2
# База данных
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sdb")
