from test.cases import cases as all_cases
from test.binary.invalid_binary_cases import cases as binary_cases
from test.mock_cases import cases as mock_cases
from test.mock_invalid_stub_cases import cases as mock_invalid_stub_cases
import os
import json
import pathlib
import signal
import traceback
import socket

should_abort = False


def socket_recv(sock: socket.socket):
    length = int.from_bytes(sock.recv(4))
    chunks = []
    length_received = 0
    print('length {}'.format(length))
    while length_received < length:
        chunk = sock.recv(min(length - length_received, 4096))
        length_received += len(chunk)
        chunks.append(chunk)
        pass
    return b''.join(chunks)


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
                return [{}, header['result']]
            elif 'throw' in header:
                return None
            else:
                return [{}, {}]


def backdoor_handler(path):
    server_socket_path = '{}/backdoor.socket'.format(path)
    if os.path.exists(server_socket_path):
        os.remove(server_socket_path)

    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(server_socket_path)
    server_socket.listen()
    while True:
        (client_socket, address) = server_socket.accept()
        try:
            # with open(fifo_ret_backdoor_path, 'r') as f:
            #     backdoor_request_json = f.read()

            backdoor_request_bytes = socket_recv(client_socket)

            if backdoor_request_bytes == b'':
                continue

            backdoor_request_json = backdoor_request_bytes.decode()

            print(' >|   {}'.format(backdoor_request_json))

            try:
                backdoor_request = json.loads(backdoor_request_json)
                backdoor_response = handler(backdoor_request)
            except Exception:
                print(traceback.format_exc())
                backdoor_response = "Boom!"

            backdoor_response_json = json.dumps(backdoor_response)

            backdoor_response_bytes = backdoor_response_json.encode()

            length = int(len(backdoor_response_bytes))

            framed_request = length.to_bytes(4) + backdoor_response_bytes

            print(' <|   {}'.format(framed_request))

            client_socket.send(framed_request)

            # with open(fifo_backdoor_path, 'w') as f:
            #     f.write(backdoor_response_json)

        except Exception:
            print(traceback.format_exc())


def signal_handler(signum, frame):
    raise Exception("Timeout")


def verify_case(runner, request, expected_response, path):
    global should_abort
    if should_abort:
        runner.skipTest('Skipped')

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(10)

    try:

        # fifo_path = '{}/frontdoor.fifo'.format(path)
        # fifo_ret_path = '{}/frontdoor_ret.fifo'.format(path)
        socket_path = '{}/frontdoor.socket'.format(path)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            while client.connect_ex(socket_path) != 0:
                pass

            if type(request) == bytes:
                request_bytes = request
            else:
                request_json = json.dumps(request)
                request_bytes = request_json.encode()

            length = int(len(request_bytes))

            framed_request = length.to_bytes(4) + request_bytes

            print(' <--| {}'.format(framed_request))

            client.send(framed_request)

            response_bytes = socket_recv(client)

            print(' -->| {}'.format(response_bytes))

            if type(expected_response) != bytes:
                response_json = response_bytes.decode()
                response = json.loads(response_json)

        print('verifying...')
    except Exception:
        traceback.print_exc()
        should_abort = True
        raise
    finally:
        signal.alarm(0)

    if type(expected_response) == bytes:
        runner.assertEqual(expected_response, response_bytes)
    else:
        runner.assertEqual(expected_response, response)


def generate():
    lib_paths = ['lib/{}'.format(f) for f in os.listdir('lib')
                 if os.path.isdir('lib/{}'.format(f))]

    for lib_path in lib_paths:
        os.makedirs('test/{}'.format(lib_path), exist_ok=True)

        if not os.path.exists('test/{}/__init__.py'.format(lib_path)):
            pathlib.Path('test/{}/__init__.py'.format(lib_path)).touch()

        generated_tests = open(
            'test/{}/test_generated.py'.format(lib_path), 'w')

        generated_tests.write('''
from generate_test import verify_case, backdoor_handler
import os
from {} import server
from {} import mock_server
import json
import unittest
import multiprocessing
                            
path = '{}'

'''.format(lib_path.replace('/', '.'), lib_path.replace('/', '.'), lib_path))
        
        generated_tests.write('''

class TestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(path, ))
        cls.process.start()                                            
        
        cls.server = server.start('../../test/example.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.join()
        cls.server.terminate()
        cls.server.wait()
                              
                        
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    def test_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path)
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
                
        generated_tests.write('''

class BinaryTestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(path, ))
        cls.process.start()                                            
        
        cls.server = server.start('../../test/binary/binary.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.process.terminate()
        cls.process.join()
        cls.server.terminate()
        cls.server.wait()
                              
                        
''')

        for name, cases in binary_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    def test_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path)
'''.format(name, i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        generated_tests.write('''

class MockTestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.server = mock_server.start('../../test/example.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()
                              
                        
''')

        for name, cases in mock_cases.items():
            generated_tests.write('''
    def test_{}(self):
'''.format(name))
            
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path)
'''.format(request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        for name, cases in mock_invalid_stub_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    def test_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path)
'''.format(name, i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))


if __name__ == '__main__':
    generate()
