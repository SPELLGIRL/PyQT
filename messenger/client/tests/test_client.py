import sys
import os
import unittest
from client import Client, parse_args
from exceptions import *

module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_dir)


class TestClient(unittest.TestCase):
    def setUp(self):
        args = parse_args()
        self.client = Client((args.addr, args.port), 'user')

    def test_username(self):
        result = self.client.validate_username('x' * 20)
        self.assertIs(type(result), str, 'Результат должен юыть строкой')

    def test_username_too_long(self):
        with self.assertRaises(SystemExit,
                               msg='Имя должно быть <= 25 символов'):
            self.client.validate_username('x' * 26)

    def test_create_presence(self):
        result = self.client.create_presence()
        self.assertIs(type(result), dict, 'результат должен быть словарём')

    def test_translate_response_type(self):
        with self.assertRaises(TypeError, msg='Ответ должен быть словарём'):
            self.client.translate_response(
                str({
                    'user': 'test',
                    'response': 200
                }))

    def test_translate_response_code(self):
        with self.assertRaises(
                MandatoryKeyError,
                msg='Не хватает обязательного атрибута response'):
            self.client.translate_response({'user': 'test'})

    def test_translate_response_code_len(self):
        with self.assertRaises(ResponseCodeLenError,
                               msg='Длина кода должна быть 3 символа'):
            self.client.translate_response({'user': 'test', 'response': 2000})

    def test_translate_response_unknown(self):
        with self.assertRaises(ResponseCodeError, msg='Неверный код ответа'):
            self.client.translate_response({'user': 'test', 'response': 199})

    def tearDown(self):
        self.client.close()


if __name__ == '__main__':
    unittest.main()
