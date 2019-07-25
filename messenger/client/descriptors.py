import logging
logger = logging.getLogger('server')


class Port:
    def __set__(self, instance, value):
        if not 1024 <= value <= 65535:
            text = f'Попытка запуска с указанием неподходящего ' \
                f'порта {value}. Допустимы адреса с 1024 до 65535.'
            logger.critical(text)
            print(text)
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name

