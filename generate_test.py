from test.cases import cases as all_cases
from test.binary.invalid_binary_cases import cases as binary_cases
from test.mock_cases import cases as mock_cases
from test.mock_invalid_stub_cases import cases as mock_invalid_stub_cases
from test.parse_cases import cases as parse_cases
from multiprocessing.managers import SharedMemoryManager
from multiprocessing.shared_memory import SharedMemory
from multiprocessing.shared_memory import ShareableList
import os
import json
import pathlib
import signal
import traceback
import socket
import msgpack
import unittest

should_abort = False


def socket_recv(sock: socket.socket):
    length = int.from_bytes(sock.recv(4))
    chunks = []
    length_received = 0
    while length_received < length:
        chunk = sock.recv(min(length - length_received, 4096))
        length_received += len(chunk)
        chunks.append(chunk)
        pass
    return b''.join(chunks)


def socket_send(sock: socket.socket, given_bytes):
    length = int(len(given_bytes))

    framed_bytes = length.to_bytes(4) + given_bytes

    sock.send(framed_bytes)    


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


def backdoor_handler(path, backdoor_results: ShareableList):
    server_socket_path = '{}/backdoor.socket'.format(path)
    if os.path.exists(server_socket_path):
        os.remove(server_socket_path)

    server_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server_socket.bind(server_socket_path)
    server_socket.listen()

    while True:
        (client_socket, address) = server_socket.accept()
        try:
            backdoor_request_bytes = socket_recv(client_socket)

            if backdoor_request_bytes == b'':
                continue

            print(' |<-    {}'.format(backdoor_request_bytes), flush=True)

            backdoor_request_json = backdoor_request_bytes.decode()

            try:
                backdoor_request = json.loads(backdoor_request_json)
                backdoor_response = handler(backdoor_request)
            except Exception:
                print(traceback.format_exc())
                backdoor_response = "Boom!"

            backdoor_response_json = json.dumps(backdoor_response)

            backdoor_response_bytes = backdoor_response_json.encode()

            print(' |->    {}'.format(backdoor_request_json), flush=True)

            socket_send(client_socket, backdoor_response_bytes)

        except Exception:
            index = backdoor_results[0]
            backdoor_results[index + 1] = 1
            print(traceback.format_exc())


def count_int_keys(m: dict):
    int_keys = 0
    str_keys = 0
    for k,v in m.items():
        if type(k) == int:
            int_keys += 1
        else:
            str_keys += 1
        if type(v) == dict:
            (this_int_keys, this_str_keys) = count_int_keys(v)
            int_keys += this_int_keys
            str_keys += this_str_keys
    return (int_keys, str_keys)


class NotEnoughIntegerKeys(Exception):
    pass


def client_backdoor_handler(path, client_backdoor_results: ShareableList):
    client_backdoor_path = '{}/clientbackdoor.socket'.format(path)
    server_frontdoor_path = '{}/frontdoor.socket'.format(path)
    if os.path.exists(client_backdoor_path):
        os.remove(client_backdoor_path)

    client_backdoor_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client_backdoor_socket.bind(client_backdoor_path)
    client_backdoor_socket.listen()
    while True:
        (client_backdoor_client, address) = client_backdoor_socket.accept()
        try:
            backdoor_request_bytes = socket_recv(client_backdoor_client)

            if backdoor_request_bytes == b'':
                continue

            print('  |<-   {}'.format(backdoor_request_bytes), flush=True)

            # try to check binary, we may not need to, but store the result anyway
            try:
                backdoor_request = msgpack.loads(backdoor_request_bytes, strict_map_key=False)
                (int_keys, str_keys) = count_int_keys(backdoor_request[1])
                if int_keys < str_keys:
                    raise NotEnoughIntegerKeys()
            except NotEnoughIntegerKeys:
                index = client_backdoor_results[0]
                client_backdoor_results[index + 1] |= 8
            except Exception:
                index = client_backdoor_results[0]
                client_backdoor_results[index + 1] |= 2


            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server_frontdoor_client:
                while server_frontdoor_client.connect_ex(server_frontdoor_path) != 0:
                    pass

                print('   |->  {}'.format(backdoor_request_bytes), flush=True)

                socket_send(server_frontdoor_client, backdoor_request_bytes)

                backdoor_response_bytes = socket_recv(server_frontdoor_client)

                print('   |<-  {}'.format(backdoor_response_bytes), flush=True)

                # try to check binary, we may not need to, but store the result anyway
                try:
                    backdoor_request = msgpack.loads(backdoor_request_bytes, strict_map_key=False)
                    (int_keys, str_keys) = count_int_keys(backdoor_request[1])
                    if int_keys < str_keys:
                        raise NotEnoughIntegerKeys()
                except NotEnoughIntegerKeys:
                    index = client_backdoor_results[0]
                    client_backdoor_results[index + 1] |= 16
                except Exception:
                    index = client_backdoor_results[0]
                    client_backdoor_results[index] |= 4


            print('  |->   {}'.format(backdoor_response_bytes), flush=True)

            socket_send(client_backdoor_client, backdoor_response_bytes)

        except Exception:
            index = client_backdoor_results[0]
            client_backdoor_results[index] |= 1
            print(traceback.format_exc())


def signal_handler(signum, frame):
    raise Exception("Timeout")


def verify_case(runner: unittest.TestCase, request, expected_response, path, backdoor_results: ShareableList | None = None, client_backdoor_results: ShareableList | None = None, client_bitmask = 0xFF, use_client=False, use_binary=False, skip_assertion=False):
    global should_abort
    if should_abort:
        if runner:
            runner.skipTest('Skipped')
        else:
            return

    if runner:
        runner.maxDiff = None

    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(30)

    if backdoor_results:
        test_index = backdoor_results[0]
        backdoor_results[test_index] = 0

    if client_backdoor_results:
        test_index = client_backdoor_results[0]
        client_backdoor_results[test_index] = 0

    try:

        if use_client:
            socket_path = '{}/clientfrontdoor.socket'.format(path)
        else:
            socket_path = '{}/frontdoor.socket'.format(path)
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
            while client.connect_ex(socket_path) != 0:
                pass

            if type(request) == bytes:
                request_bytes = request
            else:
                if use_binary:
                    request[0]['_binary'] = True

                request_json = json.dumps(request)
                request_bytes = request_json.encode()

            print('|->     {}'.format(request_bytes), flush=True)

            socket_send(client, request_bytes)

            response_bytes = socket_recv(client)

            print('|<-     {}'.format(response_bytes), flush=True)

            if type(expected_response) != bytes:
                response_json = response_bytes.decode()
                response = json.loads(response_json)

    except Exception:
        print(traceback.format_exc())
        should_abort = True
        raise
    finally:
        signal.alarm(0)

    if not skip_assertion:
        if type(expected_response) == bytes:
            runner.assertEqual(expected_response, response_bytes)
        else:
            if use_binary:
                if 'error' not in next(iter(response[1])):
                    runner.assertTrue('_bin' in response[0])
                response[0].pop('_bin', None)

            if 'numberTooBig' in response[0]:
                runner.skipTest('Cannot use big numbers with msgpack')
            
            runner.assertEqual(expected_response, response)
    
        if backdoor_results:
            test_index = backdoor_results[0]
            runner.assertEqual(0, backdoor_results[test_index])

        if client_backdoor_results:
            test_index = client_backdoor_results[0]
            runner.assertEqual(0, client_backdoor_results[test_index] & client_bitmask, """
client_bitmask
bit 0 - client proxy failed outright
bit 1 - request could not be parsed as mspack
bit 2 - response could not be parsed as mspack
bit 3 - binary request didn't have enough integer keys
bit 4 - binary response didn't have enough integer keys
""")


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
from generate_test import verify_case, backdoor_handler, client_backdoor_handler
import os
from {} import server
from {} import mock_server
from {} import schema_server
from {} import client_server
import json
import unittest
import multiprocessing
from multiprocessing.shared_memory import ShareableList

                            
path = '{}'

'''.format(lib_path.replace('/', '.'), lib_path.replace('/', '.'), lib_path.replace('/', '.'), lib_path.replace('/', '.'), lib_path))
        
        generated_tests.write('''

class TestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        initial_list = [0] * 10000
        cls.backdoor_results = ShareableList(initial_list)
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(path, cls.backdoor_results,))
        cls.process.start()                                            
        
        cls.server = server.start('../../test/example.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.backdoor_results.shm.close()
        cls.backdoor_results.shm.unlink()
        cls.process.terminate()
        cls.process.join()
        cls.server.terminate()
        cls.server.wait()

    def setUp(self):
        self.__class__.backdoor_results[0] += 1
                        
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    def test_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path, self.__class__.backdoor_results)
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
                
        generated_tests.write('''

class BinaryTestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        initial_list = [0] * 10000
        cls.backdoor_results = ShareableList(initial_list)
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(path, cls.backdoor_results,))
        cls.process.start()                                            
        
        cls.server = server.start('../../test/binary/binary.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.backdoor_results.shm.close()
        cls.backdoor_results.shm.unlink()
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
    def test_bin_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path)
'''.format(i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

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
    def test_mock_{}(self):
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
    def test_invalid_mock_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path)
'''.format(name, i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        generated_tests.write('''

class SchemaTestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.server = schema_server.start('../../test/schema.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()
                              
                        
''')

        for name, cases in parse_cases.items():
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

class ClientTestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        initial_list = [0] * 10000
        cls.backdoor_results = ShareableList(initial_list)
        cls.client_backdoor_results = ShareableList(initial_list)
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(path, cls.backdoor_results))
        cls.process.start()
        cls.client_process = multiprocessing.Process(target=client_backdoor_handler, args=(path, cls.client_backdoor_results))
        cls.client_process.start()                                                                            
        
        cls.servers = client_server.start('../../test/example.japi.json')
    
    @classmethod
    def tearDownClass(cls):
        cls.backdoor_results.shm.close()
        cls.backdoor_results.shm.unlink()
        cls.client_backdoor_results.shm.close()
        cls.client_backdoor_results.shm.unlink()
        cls.process.terminate()
        cls.process.join()
        cls.client_process.terminate()
        cls.client_process.join()
        for server in cls.servers:
            server.terminate()
        for server in cls.servers:
            server.wait()

    def setUp(self):
        self.__class__.backdoor_results[0] += 1
        self.__class__.client_backdoor_results[0] += 1
                        
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    def test_client_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path, self.__class__.backdoor_results, self.__class__.client_backdoor_results, client_bitmask=0x01, use_client=True)
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
    
        generated_tests.write('''

class BinaryClientTestCases(unittest.TestCase):
                              
    @classmethod
    def setUpClass(cls):
        initial_list = [0] * 10000
        cls.backdoor_results = ShareableList(initial_list)
        cls.client_backdoor_results = ShareableList(initial_list)
        cls.process = multiprocessing.Process(target=backdoor_handler, args=(path, cls.backdoor_results,))
        cls.process.start()
        cls.client_process = multiprocessing.Process(target=client_backdoor_handler, args=(path, cls.client_backdoor_results,))
        cls.client_process.start()                                                                            
        
        cls.servers = client_server.start('../../test/example.japi.json')
                              
        request = [{'_binary': True}, {'fn._ping': {}}]
        expected_response = [{}, {'ok':{}}]
        verify_case(None, request, expected_response, path, use_client=True, skip_assertion=True)
    
    @classmethod
    def tearDownClass(cls):
        cls.backdoor_results.shm.close()
        cls.backdoor_results.shm.unlink()
        cls.client_backdoor_results.shm.close()
        cls.client_backdoor_results.shm.unlink()
        cls.process.terminate()
        cls.process.join()
        cls.client_process.terminate()
        cls.client_process.join()
        for server in cls.servers:
            server.terminate()
        for server in cls.servers:
            server.wait()

    def setUp(self):
        self.__class__.backdoor_results[0] += 1
        self.__class__.client_backdoor_results[0] += 1
                        
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                if len(case) == 2:
                    case.append(True)
                client_bitmask = 0xFF if case[2] else 0xE7

                generated_tests.write('''
    def test_binary_client_{}_{}(self):
        request = {}
        expected_response = {}
        verify_case(self, request, expected_response, path, self.__class__.backdoor_results, self.__class__.client_backdoor_results, client_bitmask={}, use_client=True, use_binary=True)
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response, client_bitmask))
   


if __name__ == '__main__':
    generate()
