import sys
import os
import unittest
from client.client import parse_args

module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_dir)


class TestParsing(unittest.TestCase):
    def test_number_parameters(self):
        self.assertEqual(len(parse_args().__dict__), 3,
                         'Нет необходимых трёх параметров для запуска')

    def test_parameters_are_not_none(self):
        self.assertNotEqual(parse_args().addr, None,
                            'IP адрес не может быть None или Null')
        self.assertNotEqual(parse_args().port, None,
                            'Номер порта не может быть None или Null')
        self.assertNotEqual(parse_args().user, None,
                            'Имя пользователя не может быть None или Null')


if __name__ == '__main__':
    unittest.main()
