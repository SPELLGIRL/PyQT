"""Все ошибки"""


# исключение. когда имя пользователя слишком длинное - более 25 символов
class UsernameToLongError(Exception):
    """
    Класс - исключение.
    При генерации сообщает, что имя пользователя слишком длинное.
    """
    def __str__(self):
        return 'Имя пользователя должно быть менее 26 символов.'


class ResponseCodeError(Exception):
    """
    Класс - исключение.
    При генерации требует строку с неверным кодом ответа,
    полученную с сервера.
    """
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f'Неверный код ответа {self.code}.'


class ResponseCodeLenError(ResponseCodeError):
    """
    Класс - исключение.
    При генерации сообщает, что код ответа имеет неправильную длину.
    """
    def __str__(self):
        return f'Неверная длина кода {self.code}. ' \
               f'Длина кода должна быть 3 символа.'


class MandatoryKeyError(Exception):
    """
    Класс - исключение.
    При генерации требует строку с недостающим атрибутом,
    полученную с сервера.
    """
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f'Не хватает обязательного атрибута {self.key}.'


class ServerError(Exception):
    """
    Класс - исключение, для обработки ошибок сервера.
    При генерации требует строку с описанием ошибки,
    полученную с сервера.
    """
    def __init__(self, text):
        self.text = text

    def __str__(self):
        return self.text


CUSTOM_EXCEPTIONS = (UsernameToLongError, ResponseCodeError,
                     ResponseCodeLenError, MandatoryKeyError, ServerError)
