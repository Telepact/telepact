import os
from cases import cases as all_cases
from invalid_binary_cases import cases as binary_cases
from invalid_binary_cases import binary_client_rotation_cases
from mock_cases import cases as mock_cases
from mock_invalid_stub_cases import cases as mock_invalid_stub_cases
from parse_cases import cases as parse_cases


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
from test.util import verify_server_case, verify_flat_case, verify_client_case, get_nats_client, ping_req, startup_check, backdoor_handler, client_backdoor_handler, Constants as c
from {}.test_server import start_basic_server, start_mock_server, start_schema_server, start_client_server
import asyncio
import pytest
import time

'''.format(lib_path.replace('/', '.'))
        
        generated_tests_basic.write(imports)
        
        generated_tests_basic.write('''
@pytest.fixture(scope="module")
def basic_server_proc(loop, nats_server):
    s = start_basic_server(c.example_api_path, c.nats_url, 'front-basic', 'back-basic')
    
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
    s = start_basic_server(c.binary_api_path, c.nats_url, 'front-binary', 'back-binary')

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
    s = start_mock_server(c.example_api_path, c.nats_url, 'front-mock')

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
    s = start_schema_server(c.schema_api_path, c.nats_url, 'front-schema')

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
    ss = start_client_server(c.example_api_path, c.nats_url, 'cfront-client', 'cback-client', 'front-client', 'back-client')

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
    ss = start_client_server(c.example_api_path, c.nats_url, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client')
               
    try:                          
        startup_check(loop, lambda: verify_client_case(ping_req, None, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client'))
    except Exception:
        for s in ss:
            s.terminate()
        for s in ss:
            s.wait()
        raise                                         

    try:
        async def warmup():
            request = [{'_binary': True}, {'fn._ping': {}}]
            await verify_client_case(request, None, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client')

        loop.run_until_complete(warmup())
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
    print('bin_client_server_proc stopped')
    ''')

        for name, cases in all_cases.items():

            for i, case in enumerate(cases):
                request = case[0]
                expected_response = case[1]

                generated_tests_bin_client.write('''
def test_binary_client_{}_{:04d}(loop, bin_client_server_proc):
    async def t():
        request = {}
        expected_response = {}
        await verify_client_case(request, expected_response, 'cfront-bin-client', 'cback-bin-client', 'front-bin-client', 'back-bin-client', use_binary=True)
                                                 
    loop.run_until_complete(t())
'''.format(name, i, request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
   
        generated_tests_rot_bin_client = open(
            'test/{}/test_rot_bin_client_generated.py'.format(lib_path), 'w')   
        
        generated_tests_rot_bin_client.write(imports)

        generated_tests_rot_bin_client.write('''
@pytest.fixture(scope="module")
def rot_bin_client_server_proc(loop, nats_server):
    ss = start_client_server(c.example_api_path, c.nats_url, 'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client')

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

                generated_tests_rot_bin_client.write('''
        request = {}
        expected_response = {}
        await verify_client_case(request, expected_response, 'cfront-rot-bin-client', 'cback-rot-bin-client', 'front-rot-bin-client', 'back-rot-bin-client', use_binary=True)
'''.format(request.encode() if type(request) == str else request, expected_response.encode() if type(expected_response) == str else expected_response))
   
            generated_tests_rot_bin_client.write('''
    loop.run_until_complete(t())
''')


if __name__ == '__main__':
    generate()
