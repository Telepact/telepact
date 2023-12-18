from test.cases import cases as all_cases
import os
import json
import pathlib
import signal

should_abort = False

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
            
def backdoor_handler(fifo_backdoor_path):
    while True:
        with open(fifo_backdoor_path, 'r') as f:
            backdoor_request_json = f.read()    

        print(' >|   {}'.format(backdoor_request_json))

        backdoor_request = json.loads(backdoor_request_json)
        backdoor_response = handler(backdoor_request)
        backdoor_response_json = json.dumps(backdoor_response)

        with open(fifo_backdoor_path, 'w') as f:
            f.write(backdoor_response_json)

        print(' <|   {}'.format(backdoor_request_json))


def signal_handler(signum, frame):
    raise Exception("Broken")


def verify_case(runner, request, expected_response, path):
    global should_abort
    if should_abort:
        runner.skipTest('Broken')
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(1)

    try:

        fifo_path = '{}/frontdoor.fifo'.format(path)

        request_json = json.dumps(request)

        with open(fifo_path, 'w') as f:
            f.write(request_json)
        
        print(' <--| {}'.format(request_json))

        with open(fifo_path, 'r') as f:
            response_json = f.read()

        print(' -->| {}'.format(response_json))

        response = json.loads(response_json)

        runner.assertEqual(expected_response, response)
    except Exception:
        print('problem')
        should_abort = True
        raise Exception('Boom')


def generate():
    lib_paths = ['lib/{}'.format(f) for f in os.listdir('lib')
                if os.path.isdir('lib/{}'.format(f))]

    for lib_path in lib_paths:
        os.makedirs('test/{}'.format(lib_path), exist_ok=True)

        if not os.path.exists('test/{}/__init__.py'.format(lib_path)):
            pathlib.Path('test/{}/__init__.py'.format(lib_path)).touch()

        generated_tests = open('test/{}/test_generated.py'.format(lib_path), 'w')

        generated_tests.write('''
from generate_test import verify_case, backdoor_handler
import os
from {} import server
import json
import unittest
import multiprocessing
                            
path = '{}'
fifo_path = '{}/frontdoor.fifo'
fifo_backdoor_path = '{}/backdoor.fifo'

class TestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(fifo_path):
            os.mkfifo(fifo_path)
        if not os.path.exists(fifo_backdoor_path):
            os.mkfifo(fifo_backdoor_path)
        
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(fifo_backdoor_path, ))
        cls.process.start()                                            
        
        cls.server = server.start('../../test/example.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.server.terminate()
        os.remove(fifo_path)                              
        os.remove(fifo_backdoor_path)
                              
                        
    '''.format(lib_path.replace('/', '.'), lib_path, lib_path, lib_path))

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