from test.cases import cases as all_cases
import os
import json
import pathlib
import signal
import traceback

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
            
def backdoor_handler(fifo_backdoor_path, fifo_ret_backdoor_path):
    while True:
        try:
            with open(fifo_ret_backdoor_path, 'r') as f:
                backdoor_request_json = f.read()    

            print(' >|   {}'.format(backdoor_request_json))

            try:
                backdoor_request = json.loads(backdoor_request_json)
                backdoor_response = handler(backdoor_request)
            except Exception:
                print(traceback.format_exc())
                backdoor_response = "Boom!"

            backdoor_response_json = json.dumps(backdoor_response)

            print(' <|   {}'.format(backdoor_response_json))

            with open(fifo_backdoor_path, 'w') as f:
                f.write(backdoor_response_json)

        except Exception:
            print(traceback.format_exc())


def signal_handler(signum, frame):
    raise Exception("Timeout")


def verify_case(runner, request, expected_response, path):
    global should_abort
    if should_abort:
        runner.skipTest('Skipped')
    
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(5)

    try:

        fifo_path = '{}/frontdoor.fifo'.format(path)
        fifo_ret_path = '{}/frontdoor_ret.fifo'.format(path)

        request_json = json.dumps(request)

        print(' <--| {}'.format(request_json))

        with open(fifo_path, 'w') as f:
            f.write(request_json)
        
        with open(fifo_ret_path, 'r') as f:
            response_json = f.read()

        print(' -->| {}'.format(response_json))

        response = json.loads(response_json)

        runner.assertEqual(expected_response, response)
    except Exception:
        traceback.print_exc()
        should_abort = True
        raise
    finally:
        signal.alarm(0)


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
fifo_ret_path = '{}/frontdoor_ret.fifo'
fifo_ret_backdoor_path = '{}/backdoor_ret.fifo'

class TestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        if not os.path.exists(fifo_path):
            os.mkfifo(fifo_path)
        if not os.path.exists(fifo_backdoor_path):
            os.mkfifo(fifo_backdoor_path)
        if not os.path.exists(fifo_ret_path):
            os.mkfifo(fifo_ret_path)
        if not os.path.exists(fifo_ret_backdoor_path):
            os.mkfifo(fifo_ret_backdoor_path)
        
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(fifo_backdoor_path, fifo_ret_backdoor_path, ))
        cls.process.start()                                            
        
        cls.server = server.start('../../test/example.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.server.terminate()
        os.remove(fifo_path)                              
        os.remove(fifo_backdoor_path)
        os.remove(fifo_ret_path)                              
        os.remove(fifo_ret_backdoor_path)
                              
                        
    '''.format(lib_path.replace('/', '.'), lib_path, lib_path, lib_path, lib_path, lib_path))

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