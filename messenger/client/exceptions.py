"""Все ошибки"""


# исключение. когда имя пользователя слишком длинное - более 25 символов
class UsernameToLongError(Exception):
    def __str__(self):
        return 'Имя пользователя должно быть менее 26 символов.'


# исключение. переданный код отсутствует среди стандартных кодов
class ResponseCodeError(Exception):
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return f'Неверный код ответа {self.code}.'


# исключение. длина кода - не три символа
class ResponseCodeLenError(ResponseCodeError):
    def __str__(self):
        return f'Неверная длина кода {self.code}. ' \
            f'Длина кода должна быть 3 символа.'


# исключение. отсутствует обязательный атрибут response
class MandatoryKeyError(Exception):
    def __init__(self, key):
        self.key = key

    def __str__(self):
        return f'Не хватает обязательного атрибута {self.key}.'


CUSTOM_EXCEPTIONS = (
    UsernameToLongError, ResponseCodeError, ResponseCodeLenError,
    MandatoryKeyError
)
