"""Константы для jim протокола, настройки"""
# Формат даты
DATE_FORMAT = '%d-%m-%Y %H:%M'
# Разделитель сообщений
DELIMITER = '\0'

# Ключи
# тип сообщения между клиентом и сервером
ACTION = 'action'
# время запроса
TIME = 'time'
# данные о пользователе - клиенте
USER = 'user_name'
# код ответа
RESPONSE = 'response'
# кому
TO = 'to'
# от кого
FROM = 'sender'
# сообщение
TEXT = 'text'
# Количество
QUANTITY = 'quantity'
# текст ошибки
ERROR = 'error'

# Значения
PRESENCE = 'presence'
REGISTER = 'register'
AUTH = 'auth'
SEND_MSG = 'send_msg'
GET_CONTACTS = 'get_contacts'
GET_CONNECTED = 'get_connected'
ADD_CONTACT = 'add_contact'
DEL_CONTACT = 'del_contact'
READ_MESSAGES = 'read_messages'

# Коды ответов
BASIC_NOTICE = 100
OK = 200
ACCEPTED = 202
WRONG_REQUEST = 400  # неправильный запрос/json объект
FORBIDDEN = 403  # доступ запрещён
SERVER_ERROR = 500

# Кортеж из кодов ответов
RESPONSE_CODES = (BASIC_NOTICE, OK, ACCEPTED, WRONG_REQUEST, SERVER_ERROR)
