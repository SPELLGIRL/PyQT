import sys
import os
import unittest
import time
from server import Server, parse_args

module_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(module_dir)


class TestServer(unittest.TestCase):
    def setUp(self):
        args = parse_args()
        self.server = Server((args.a, args.p))

    def test_create_response_success(self):
        self.assertEqual(
            self.server.create_response({
                'action': 'presence',
                'time': time.time()
            }), {'response': 200})

    def test_create_response_error(self):
        self.assertEqual(
            self.server.create_response({
                'action': 'random',
                'time': time.time()
            }), {
                'response': 400,
                'error': 'Не верный запрос.'
            })

    def tearDown(self):
        self.server.close()


if __name__ == '__main__':
    unittest.main()
