from test.cases import cases as all_cases
import os
import json
import pathlib

def handler(request):
    header = request[0]
    body = request[1]
    target = next(iter(body))
    payload = body[target]

    match target:
        case 'fn.test':
            if 'ok' in header:
                return [{}, {'ok': header['ok']}]
            elif 'result' in header:
                return header['result']
            elif 'throw' in header:
                return None
            else:
                return [{}, {}]

def verify_case(runner, request, expected_response, path):
    fifo_path = '{}/transport.fifo'.format(path)

    request_json = json.dumps(request)

    with open(fifo_path, 'w') as f:
        f.write(request_json)

    print(' <--| {}'.format(request_json))

    with open(fifo_path, 'r') as f:
        backdoor_request_json = f.read()

    print(' >| {}'.format(backdoor_request_json))

    backdoor_request = json.loads(backdoor_request_json)
    backdoor_response = handler(backdoor_request)
    backdoor_response_json = json.dumps(backdoor_response)

    with open(fifo_path, 'w') as f:
        f.write(backdoor_response_json)

    print(' <| {}'.format(backdoor_request_json))

    with open(fifo_path, 'r') as f:
        response_json = f.read()

    print(' -->| {}'.format(response_json))

    response = json.loads(response_json)

    runner.assertEqual(expected_response, response)


def generate():
    lib_paths = ['lib/{}'.format(f) for f in os.listdir('lib')
                if os.path.isdir('lib/{}'.format(f))]

    for lib_path in lib_paths:
        os.makedirs('test/{}'.format(lib_path), exist_ok=True)

        if not os.path.exists('test/{}/__init__.py'.format(lib_path)):
            pathlib.Path('test/{}/__init__.py'.format(lib_path)).touch()

        generated_tests = open('test/{}/test_generated.py'.format(lib_path), 'w')

        generated_tests.write('''
from generate_test import verify_case
import os
from {} import server
import json
import unittest
                            
path = '{}'
fifo_path = '{}/transport.fifo'

class TestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(fifo_path):
            os.mkfifo(fifo_path)
        
        cls.server = server.start('../../test/example.japi.json')
    
    @classmethod
    def tearDown(cls):
        cls.server.terminate()
        os.remove(fifo_path)                              
                        
    '''.format(lib_path.replace('/', '.'), lib_path, lib_path))

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                generated_tests.write('''
    def test_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path)
    '''.format(name, i, case[0], case[1]))


if __name__ == '__main__':
    generate()