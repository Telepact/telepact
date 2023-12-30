from test.cases import cases as all_cases
from test.invalid_binary_cases import cases as binary_cases
from test.invalid_binary_cases import binary_client_rotation_cases
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
import nats
import asyncio
import subprocess

should_abort = False

class Constants:
    example_api_path = '../../test/example.japi.json'
    binary_api_path = '../../test/binary/binary.japi.json'
    schema_api_path = '../../test/schema.japi.json'
    nats_url = 'nats://127.0.0.1:4222'
    frontdoor_topic = 'frontdoor'
    intermediate_topic = 'intermediate'
    backdoor_topic = 'backdoor'


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
            if 'Ok' in header:
                return [{}, {'Ok': header['Ok']}]
            elif 'result' in header:
                return [{}, header['result']]
            elif 'throw' in header:
                return None
            else:
                return [{}, {}]


async def old_backdoor_handler(path, backdoor_results: ShareableList):
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


async def backdoor_handler(backdoor_topic):
    nats_client = await get_nats_client()

    async def nats_handler(msg):
        backdoor_request_bytes = msg.data
        backdoor_request_json = backdoor_request_bytes.decode()
        backdoor_request = json.loads(backdoor_request_json)

        print(' |<-    {}'.format(backdoor_request), flush=True)

        backdoor_response = handler(backdoor_request)

        print(' |->    {}'.format(backdoor_response), flush=True)

        backdoor_response_json = json.dumps(backdoor_response)
        backdoor_response_bytes = backdoor_response_json.encode()        
        await nats_client.publish(msg.reply, backdoor_response_bytes)

    sub = await nats_client.subscribe(backdoor_topic, cb=nats_handler)

    await sub.unsubscribe(limit=1)


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


def old_client_backdoor_handler(path, client_backdoor_results: ShareableList):
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


async def client_backdoor_handler(path, client_frontdoor_topic, server_frontdoor_topic):
    nats_client = await get_nats_client()

    async def nats_handler(msg):
        frontdoor_request_bytes = msg.data
        try:
            frontdoor_request_json = frontdoor_request_bytes.decode()
            frontdoor_request = json.loads(frontdoor_request_json)
        except Exception:
            frontdoor_request = msgpack.loads(frontdoor_request_bytes, strict_map_key=False)
            # TODO: Verify binary is done when it's supposed to be done

        print('  |<-   {}'.format(frontdoor_request), flush=True)
        print('   |->  {}'.format(frontdoor_request), flush=True)

        frontdoor_response_bytes = await nats_client.request(server_frontdoor_topic, frontdoor_request_bytes, timeout=10)

        try:
            frontdoor_response_json = frontdoor_response_bytes.decode()
            frontdoor_response = json.loads(frontdoor_response_json)
        except Exception:
            frontdoor_response = msgpack.loads(frontdoor_response_bytes, strict_map_key=False)
            # TODO: verify binary is done when it's supposed to be done

        print('   |<-  {}'.format(frontdoor_response), flush=True)
        print('  |->   {}'.format(frontdoor_response), flush=True)

        await nats_client.publish(msg.reply, frontdoor_response_bytes)

    sub = await nats_client.subscribe(client_frontdoor_topic, cb=nats_handler)

    await sub.unsubscribe(limit=1)


def signal_handler(signum, frame):
    raise Exception("Timeout")


nc = None

async def get_nats_client():
    global nc
    if not nc:
        nc = await nats.connect(Constants.nats_url) 
    return nc


def start_nats_server():
    return subprocess.Popen(['nats-server', '-DV'])


async def verify_basic_case(runner: unittest.TestCase, request, expected_response):

    backdoor_handling_task = asyncio.create_task(backdoor_handler(Constants.backdoor_topic))

    response = await send_case(runner, request, expected_response, Constants.frontdoor_topic)

    backdoor_handling_task.cancel()

    runner.assertEqual(expected_response, response)


async def verify_flat_case(runner: unittest.TestCase, request, expected_response):

    response = await send_case(runner, request, expected_response, Constants.frontdoor_topic)

    runner.assertEqual(expected_response, response)


async def verify_client_case(runner: unittest.TestCase, request, expected_response, use_binary=False, enforce_binary=False, enforce_integer_keys=False):

    client_handling_task = asyncio.create_task(client_backdoor_handler(Constants.intermediate_topic))    
    backdoor_handling_task = asyncio.create_task(backdoor_handler(Constants.backdoor_topic))

    if use_binary:
        request[0]['_binary'] = True

    response = await send_case(runner, request, expected_response, Constants.frontdoor_topic)

    backdoor_handling_task.cancel()
    client_handling_task.cancel()

    if use_binary:
        if 'Error' not in next(iter(response[1])):
            runner.assertTrue('_bin' in response[0])
        response[0].pop('_bin', None)
        response[0].pop('_enc', None)
    
    runner.assertEqual(expected_response, response)

    # TODO: verify that binary was being done    
            

async def binary_client_warmup(request, expected_response):

    client_handling_task = asyncio.create_task(client_backdoor_handler(Constants.intermediate_topic))
    backdoor_handling_task = asyncio.create_task(backdoor_handler(Constants.backdoor_topic))

    response = await send_case(None, request, expected_response, Constants.frontdoor_topic)

    backdoor_handling_task.cancel()
    client_handling_task.cancel()


async def send_case(runner: unittest.TestCase, request, expected_response, request_topic):
    global should_abort
    if should_abort:
        if runner:
            runner.skipTest('Skipped')
        else:
            return
        
    nats_client = await get_nats_client()

    if runner:
        runner.maxDiff = None

    print('|->     {}'.format(request), flush=True)

    if type(request) == bytes:
        request_bytes = request
    else:
        request_json = json.dumps(request)
        request_bytes = request_json.encode()    

    nats_response = await nats_client.request(request_topic, request_bytes, timeout=1)

    response_bytes = nats_response.data

    if type(expected_response) == bytes:
        response = response_bytes
    else:
        response_json = response_bytes.decode()
        response = json.loads(response_json)    

    print('|<-     {}'.format(response), flush=True)

    if 'numberTooBig' in response[0]:
        runner.skipTest('Cannot use big numbers with msgpack')    

    return response


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
from generate_test import verify_basic_case, verify_flat_case, verify_client_case, binary_client_warmup, start_nats_server, backdoor_handler, client_backdoor_handler, Constants as c
import os
from {} import server
from {} import mock_server
from {} import schema_server
from {} import client_server
import json
import unittest
import multiprocessing
from multiprocessing.shared_memory import ShareableList
import asyncio

                            
path = '{}'

'''.format(lib_path.replace('/', '.'), lib_path.replace('/', '.'), lib_path.replace('/', '.'), lib_path.replace('/', '.'), lib_path))
        
        generated_tests.write('''

class TestCases(unittest.IsolatedAsyncioTestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.nats = start_nats_server()
        try:
            cls.server = server.start(c.example_api_path, c.nats_url, c.frontdoor_topic, c.backdoor_topic)
        except Exception:
            cls.nats.terminate()
            cls.nats.wait()
            raise
    
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()
        cls.nats.terminate()
        cls.nats.wait()

    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    async def test_{}_{:04d}(self):
        request = {}
        expected_response = {}
        await verify_basic_case(self, request, expected_response)
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
                
        generated_tests.write('''

class BinaryTestCases(unittest.IsolatedAsyncioTestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.nats = start_nats_server()
        try:
            cls.server = server.start(c.binary_api_path, c.nats_url, c.frontdoor_topic)
        except Exception:
            cls.nats.terminate()
            cls.nats.wait()
            raise
    
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()
        cls.nats.terminate()
        cls.nats.wait()
                              
                        
''')

        for name, cases in binary_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    async def test_bin_{:04d}(self):
        request = {}
        expected_response = {}
        await verify_basic_case(self, request, expected_response)
'''.format(i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        generated_tests.write('''

class MockTestCases(unittest.IsolatedAsyncioTestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.nats = start_nats_server()
        try:
            cls.server = mock_server.start(c.example_api_path, c.nats_url, c.frontdoor_topic)
        except Exception:
            cls.nats.terminate()
            cls.nats.wait()
            raise
    
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()
        cls.nats.terminate()
        cls.nats.wait()
                              
                        
''')

        for name, cases in mock_cases.items():
            generated_tests.write('''
    async def test_mock_{}(self):
'''.format(name))
            
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
        request = {}
        expected_response = {}
        await verify_flat_case(self, request, expected_response)
'''.format(request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        for name, cases in mock_invalid_stub_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    async def test_invalid_mock_{}_{:04d}(self):
        request = {}
        expected_response = {}
        await verify_flat_case(self, request, expected_response)
'''.format(name, i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        generated_tests.write('''

class SchemaTestCases(unittest.IsolatedAsyncioTestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.nats = start_nats_server()
        try:
            cls.server = schema_server.start(c.schema_api_path, c.nats_url, c.frontdoor_topic)
        except Exception:
            cls.nats.terminate()
            cls.nats.wait()
            raise
    
    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.wait()
        cls.nats.terminate()
        cls.nats.wait()
                              
                        
''')

        for name, cases in parse_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    async def test_{}_{:04d}(self):
        request = {}
        expected_response = {}
        await verify_flat_case(self, request, expected_response)
'''.format(name, i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))


        generated_tests.write('''

class ClientTestCases(unittest.IsolatedAsyncioTestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.nats = start_nats_server()
        try:
            cls.servers = client_server.start(c.example_api_path, c.nats_url, c.frontdoor_topic, c.intermediate_topic, c.backdoor_topic)
        except Exception:
            cls.nats.terminate()
            cls.nats.wait()
            raise

    @classmethod
    def tearDownClass(cls):
        for server in cls.servers:
            server.terminate()
        for server in cls.servers:
            server.wait()
        cls.nats.terminate()
        cls.nats.wait()
                        
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests.write('''
    async def test_client_{}_{:04d}(self):
        request = {}
        expected_response = {}
        await verify_client_case(self, request, expected_response, path, self.__class__.backdoor_results, self.__class__.client_backdoor_results, client_bitmask=0x01, use_client=True)
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
    
        generated_tests.write('''

class BinaryClientTestCases(unittest.IsolatedAsyncioTestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.nats = start_nats_server()
        try:
            cls.servers = client_server.start(c.example_api_path, c.nats_url, c.frontdoor_topic, c.intermediate_topic, c.backdoor_topic)
        except Exception:
            cls.nats.terminate()
            cls.nats.wait()
            raise
                              
        request = [{'_binary': True}, {'fn._ping': {}}]
        expected_response = [{}, {'Ok':{}}]
        binary_client_warmup(request, expected_response)
    
    @classmethod
    def tearDownClass(cls):
        for server in cls.servers:
            server.terminate()
        for server in cls.servers:
            server.wait()
        cls.nats.terminate()
        cls.nats.wait()
                        
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                if len(case) == 2:
                    case.append(True)
                client_bitmask = 0xFF if case[2] else 0xE7

                generated_tests.write('''
    async def test_binary_client_{}_{:04d}(self):
        request = {}
        expected_response = {}
        await verify_client_case(self, request, expected_response, path, self.__class__.backdoor_results, self.__class__.client_backdoor_results, client_bitmask={}, use_client=True, use_binary=True)
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response, client_bitmask))
   

        generated_tests.write('''

class RotateBinaryClientTestCases(unittest.IsolatedAsyncioTestCase):
                              
    @classmethod
    def setUpClass(cls):
        cls.nats = start_nats_server()
        try:
            cls.servers = client_server.start(c.example_api_path, c.nats_url, c.frontdoor_topic, c.intermediate_topic, c.backdoor_topic)
        except Exception:
            cls.nats.terminate()
            cls.nats.wait()
            raise
            
                              
    @classmethod
    def tearDownClass(cls):
        for server in cls.servers:
            server.terminate()
        for server in cls.servers:
            server.wait()
        cls.nats.terminate()
        cls.nats.wait()
                        
    ''')
        
        for name, cases in binary_client_rotation_cases.items():
            generated_tests.write('''
    async def test_rotate_binary_client_{}(self):
'''.format(name))

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                if len(case) == 2:
                    case.append(True)
                client_bitmask = 0xFF if case[2] else 0x01

                generated_tests.write('''

        request = {}
        expected_response = {}
        await verify_client_case(self, request, expected_response, path, self.__class__.backdoor_results, self.__class__.client_backdoor_results, client_bitmask={}, use_client=True, use_binary=True)
'''.format(request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response, client_bitmask))
   



if __name__ == '__main__':
    generate()
