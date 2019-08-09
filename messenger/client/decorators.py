from functools import wraps
import traceback


class Log:
    """
    Класс декоратор для логирования функций
    """
    def __init__(self, logger):
        self._func = None
        self._obj = None
        # запоминаем логгер, чтобы можно было использовать разные
        self._logger = logger

    def __call__(self, func):
        def decorator(*args, **kwargs):
            self._func = func
            if len(self._func.__qualname__.split('.')) > 1:
                return self._wrap_method(self._func)(*args, **kwargs)
            else:
                return self._wrap_function(self._func)(*args, **kwargs)

        return decorator

    def __get__(self, obj, owner=None):
        self._obj = obj
        return self

    def _wrap_method(self, method):
        @wraps(method)
        def inner(first_arg, *args, **kwargs):
            result = method(first_arg, *args, **kwargs)
            message = self._create_message(result, *args, **kwargs)
            self._logger.info(
                f'{message} // метод {method.__name__} класса '
                f'{method.__qualname__.split(".")[0]} {self._info}')
            return result

        return inner

    def _wrap_function(self, function):
        @wraps(function)
        def inner(*args, **kwargs):
            result = function(*args, **kwargs)
            message = Log._create_message(result, *args, **kwargs)
            self._logger.info(
                f'{message} // функция {function.__name__} {self._info}')
            return result

        return inner

    @property
    def _info(self):
        string = list(
            filter(None, [
                i if self._func.__name__ in i else None
                for i in traceback.format_stack()
            ]))[0]
        _line = string.strip().split(',')[1].split()[-1]
        _filename = \
            string.strip().split('"')[1].replace('/', '\\').split('\\')[-1]
        return f'в модуле {_filename} на строке {_line}'

    @staticmethod
    def _create_message(result=None, *args, **kwargs):
        """
        Формирует сообщение для записи в лог
        :param result: результат работы функции
        :param args: любые параметры по порядку
        :param kwargs: любые именованные параметры
        :return:
        """

        message = ''
        if args:
            message += f'args: {str(args).replace(",)", ")")} '
        if kwargs:
            message += f'kwargs: {kwargs}'
        if result:
            message += f' result: {result}'
        # Возвращаем итоговое сообщение
        return message
