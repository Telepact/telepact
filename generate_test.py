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
import pytest
import nats.aio.client
import time

should_abort = False

class Constants:
    example_api_path = '../../test/example.japi.json'
    binary_api_path = '../../test/binary/binary.japi.json'
    schema_api_path = '../../test/schema.japi.json'
    nats_url = 'nats://127.0.0.1:4222'
    frontdoor_topic = 'frontdoor'
    intermediate_topic = 'intermediate'
    backdoor_topic = 'backdoor'

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


async def backdoor_handler(backdoor_topic):
    nats_client = await get_nats_client()

    async def nats_handler(msg):
        backdoor_request_bytes = msg.data
        backdoor_request_json = backdoor_request_bytes.decode()
        backdoor_request = json.loads(backdoor_request_json)

        print(' B<-    {}'.format(backdoor_request), flush=True)

        backdoor_response = handler(backdoor_request)

        print(' B->    {}'.format(backdoor_response), flush=True)

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



async def client_backdoor_handler(client_backdoor_topic, frontdoor_topic, times=1):
    nats_client = await get_nats_client()

    async def nats_handler(msg):
        client_backdoor_request_bytes = msg.data
        try:
            client_backdoor_request_json = client_backdoor_request_bytes.decode()
            client_backdoor_request = json.loads(client_backdoor_request_json)
        except Exception:
            client_backdoor_request = msgpack.loads(client_backdoor_request_bytes, strict_map_key=False)
            # TODO: Verify binary is done when it's supposed to be done

        print('  I<-   {}'.format(client_backdoor_request), flush=True)
        print('  i->   {}'.format(client_backdoor_request), flush=True)

        nats_response = await nats_client.request(frontdoor_topic, client_backdoor_request_bytes, timeout=10)

        frontdoor_response_bytes = nats_response.data

        try:
            frontdoor_response_json = frontdoor_response_bytes.decode()
            frontdoor_response = json.loads(frontdoor_response_json)
        except Exception:
            frontdoor_response = msgpack.loads(frontdoor_response_bytes, strict_map_key=False)
            # TODO: verify binary is done when it's supposed to be done

        print('  i<-   {}'.format(frontdoor_response), flush=True)
        print('  I->   {}'.format(frontdoor_response), flush=True)

        await nats_client.publish(msg.reply, frontdoor_response_bytes)

    sub = await nats_client.subscribe(client_backdoor_topic, cb=nats_handler)

    await sub.unsubscribe(limit=times)


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


async def verify_server_case(request, expected_response, frontdoor_topic, backdoor_topic):

    backdoor_handling_task = asyncio.create_task(backdoor_handler(backdoor_topic))

    try:
        response = await send_case(request, expected_response, frontdoor_topic)
    finally:
        backdoor_handling_task.cancel()
        await backdoor_handling_task

    if expected_response:
        assert expected_response == response


async def verify_flat_case(request, expected_response, frontdoor_topic):

    response = await send_case(request, expected_response, frontdoor_topic)

    if expected_response:
        assert expected_response == response


async def verify_client_case(request, expected_response, client_frontdoor_topic, client_backdoor_topic, frontdoor_topic, backdoor_topic, use_binary=False, enforce_binary=False, enforce_integer_keys=False, times=1):

    client_handling_task = asyncio.create_task(client_backdoor_handler(client_backdoor_topic, frontdoor_topic, times=times))    
    backdoor_handling_task = asyncio.create_task(backdoor_handler(backdoor_topic))

    if use_binary:
        request[0]['_binary'] = True

    try:
        response = await send_case(request, expected_response, client_frontdoor_topic)
    finally:
        backdoor_handling_task.cancel()
        client_handling_task.cancel()
        await backdoor_handling_task
        await client_handling_task

    if use_binary:
        if 'Error' not in next(iter(response[1])):
            assert '_bin' in response[0]
        response[0].pop('_bin', None)
        response[0].pop('_enc', None)

    if expected_response:
        assert expected_response == response

    # TODO: verify that binary was being done    


async def send_case(request, expected_response, request_topic):
    nats_client = await get_nats_client()

    print('T->     {}'.format(request), flush=True)

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

    print('T<-     {}'.format(response), flush=True)

    if 'numberTooBig' in response[0]:
        pytest.skip('Cannot use big numbers with msgpack')

    return response

ping_req = [{},{'fn._ping': {}}]

def startup_check(loop: asyncio.AbstractEventLoop, verify):
    async def check():
        ex: Exception = None
        for _ in range(10):
            try:
                await verify()
                print('Server successfully started.')
                return
            except Exception as e:
                ex = e
                print('Server not yet ready...')
                print(e)
                time.sleep(1)
        
        raise Exception('Server did not startup correctly') from ex
    
    loop.run_until_complete(check())


def generate():
    lib_paths = ['lib/{}'.format(f) for f in os.listdir('lib')
                 if os.path.isdir('lib/{}'.format(f))]

    for lib_path in lib_paths:
        os.makedirs('test/{}'.format(lib_path), exist_ok=True)

        init = open('test/{}/__init__.py'.format(lib_path), 'w')
        init.write('''
''')

        generated_tests_basic = open(
            'test/{}/test_basic_generated.py'.format(lib_path), 'w')

        imports = '''
from generate_test import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c
from {} import server, mock_server, schema_server, client_server
import asyncio
import pytest
import time

'''.format(lib_path.replace('/', '.'))
        
        generated_tests_basic.write(imports)
        
        generated_tests_basic.write('''
@pytest.fixture(scope="module")
def basic_server_proc(loop, nats_server):
    s = server.start(c.example_api_path, c.nats_url, 'front-basic', 'back-basic')
    
    try:                                
        startup_check(loop, lambda: verify_server_case(ping_req, None, 'front-basic', 'back-basic'))
    except Exception:
        s.terminate()
        s.wait()
        raise   
    
    yield s
    s.terminate()
    s.wait()
    print('basic_server_proc stopped')

''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests_basic.write('''
def test_{}_{:04d}(loop, basic_server_proc):
    async def t():
        request = {}
        expected_response = {}
        await verify_server_case(request, expected_response, 'front-basic', 'back-basic')
    
    loop.run_until_complete(t())
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))

        generated_tests_binary = open(
            'test/{}/test_binary_generated.py'.format(lib_path), 'w') 
        
        generated_tests_binary.write(imports)

        generated_tests_binary.write('''
@pytest.fixture(scope="module")
def binary_server_proc(loop, nats_server):
    s = server.start(c.binary_api_path, c.nats_url, 'front-binary', 'back-binary')

    try:
        startup_check(loop, lambda: verify_server_case(ping_req, None, 'front-binary', 'back-binary'))
    except Exception:
        s.terminate()
        s.wait()
        raise    

    yield s
    s.terminate()
    s.wait()
    print('binary_server_proc stopped')
''')

        for name, cases in binary_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests_binary.write('''
def test_bin_{:04d}(loop, binary_server_proc):
    async def t():
        request = {}
        expected_response = {}
        await verify_server_case(request, expected_response, 'front-binary', 'back-binary')
    
    loop.run_until_complete(t())
'''.format(i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        generated_tests_mock = open(
            'test/{}/test_mock_generated.py'.format(lib_path), 'w')    

        generated_tests_mock.write(imports)

        generated_tests_mock.write('''
@pytest.fixture(scope="module")
def mock_server_proc(loop, nats_server):
    s = mock_server.start(c.example_api_path, c.nats_url, 'front-mock')

    try:
        startup_check(loop, lambda: verify_flat_case(ping_req, None, 'front-mock'))
    except Exception:
        s.terminate()
        s.wait()
        raise      

    yield s
    s.terminate()
    s.wait()
    print('mock_server_proc stopped')
''')

        for name, cases in mock_cases.items():
            generated_tests_mock.write('''
def test_mock_{}(loop, mock_server_proc):
    async def t():
'''.format(name))
            
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests_mock.write('''
        request = {}
        expected_response = {}
        await verify_flat_case(request, expected_response, 'front-mock')
'''.format(request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))
                
            generated_tests_mock.write('''

    loop.run_until_complete(t())
''')

        for name, cases in mock_invalid_stub_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests_mock.write('''
def test_invalid_mock_{}_{:04d}(loop, mock_server_proc):
    async def t():
        request = {}
        expected_response = {}
        await verify_flat_case(request, expected_response, 'front-mock')
    
    loop.run_until_complete(t())
'''.format(name, i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        generated_tests_schema = open(
            'test/{}/test_schema_generated.py'.format(lib_path), 'w')

        generated_tests_schema.write(imports)

        generated_tests_schema.write('''
@pytest.fixture(scope="module")
def schema_server_proc(loop, nats_server):
    s = schema_server.start(c.schema_api_path, c.nats_url, 'front-schema')

    try:
        startup_check(loop, lambda: verify_flat_case(ping_req, None, 'front-schema'))
    except Exception:
        s.terminate()
        s.wait()
        raise      

    yield s
    s.terminate()
    s.wait()
    print('schema_server_proc stopped')
''')

        for name, cases in parse_cases.items():
            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests_schema.write('''
def test_schema_{}_{:04d}(loop, schema_server_proc):
    async def t():
        request = {}
        expected_response = {}
        await verify_flat_case(request, expected_response, 'front-schema')
                                             
    loop.run_until_complete(t())
'''.format(name, i, request.encode('raw_unicode_escape') if type(request) == str else request, expected_response.encode('raw_unicode_escape') if type(expected_response) == str else expected_response))

        generated_tests_client = open(
            'test/{}/test_client_generated.py'.format(lib_path), 'w')  

        generated_tests_client.write(imports)  

        generated_tests_client.write('''
@pytest.fixture(scope="module")
def client_server_proc(loop, nats_server):
    ss = client_server.start(c.example_api_path, c.nats_url, 'cfront-client', 'cback-client', 'front-client', 'back-client')

    try:
        startup_check(loop, lambda: verify_client_case(ping_req, None, 'cfront-client', 'cback-client', 'front-client', 'back-client'))
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise                                         

    yield ss
    for s in ss:
        s.terminate()
    for s in ss:
        s.wait()
    print('client_server_proc stopped')
''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests_client.write('''
def test_client_{}_{:04d}(loop, client_server_proc):
    async def t():
        request = {}
        expected_response = {}
        await verify_client_case(request, expected_response, 'cfront-client', 'cback-client', 'front-client', 'back-client')
                                             
    loop.run_until_complete(t())
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
    
        generated_tests_bin_client = open(
            'test/{}/test_bin_client_generated.py'.format(lib_path), 'w')   

        generated_tests_bin_client.write(imports)   

        generated_tests_bin_client.write('''
@pytest.fixture(scope="module")
def bin_client_server_proc(loop, nats_server):
    ss = client_server.start(c.example_api_path, c.nats_url, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client')
               
    try:                          
        startup_check(loop, lambda: verify_client_case(ping_req, None, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client'))
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise                                         

    async def warmup():
        request = [{'_binary': True}, {'fn._ping': {}}]
        await verify_client_case(request, None, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client')

    loop.run_until_complete(warmup())
    
    yield ss
    for s in ss:
        s.terminate()
    for s in ss:
        s.wait()                        
    print('bin_client_server_proc stopped')
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                if len(case) == 2:
                    case.append(True)

                generated_tests_bin_client.write('''
def test_binary_client_{}_{:04d}(loop, bin_client_server_proc):
    async def t():
        request = {}
        expected_response = {}
        await verify_client_case(request, expected_response, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client', use_binary=True, enforce_binary=True, enforce_integer_keys={})
                                                 
    loop.run_until_complete(t())
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response, case[2]))
   
        generated_tests_rot_bin_client = open(
            'test/{}/test_rot_bin_client_generated.py'.format(lib_path), 'w')   
        
        generated_tests_rot_bin_client.write(imports)

        generated_tests_rot_bin_client.write('''
@pytest.fixture(scope="module")
def rot_bin_client_server_proc(loop, nats_server):
    ss = client_server.start(c.example_api_path, c.nats_url, 'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client')

    try:
        startup_check(loop, lambda: verify_client_case(ping_req, None,  'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client'))
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise
                                             
    yield ss
    for s in ss:
        s.terminate()
    for s in ss:
        s.wait()    
    print('rot_bin_client_server_proc stopped')
    ''')
        
        for name, cases in binary_client_rotation_cases.items():
            generated_tests_rot_bin_client.write('''
def test_rotate_binary_client_{}(loop, rot_bin_client_server_proc):
    async def t():
'''.format(name))

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                if len(case) == 2:
                    case.append(True)

                generated_tests_rot_bin_client.write('''
        request = {}
        expected_response = {}
        await verify_client_case(request, expected_response, 'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client', use_binary=True, enforce_binary={}, times=2)
'''.format(request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response, case[2]))
   
            generated_tests_rot_bin_client.write('''
    loop.run_until_complete(t())
''')


if __name__ == '__main__':
    generate()
