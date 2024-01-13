import subprocess
import pytest
import asyncio
from test.cases import cases as basic_cases
from test.binary_cases import cases as binary_cases
from test.binary_cases import binary_client_rotation_cases
from test.mock_cases import cases as mock_cases
from test.mock_cases import invalid_cases as mock_invalid_cases
from test.parse_cases import cases as parse_cases
from copy import deepcopy as dc
from test.util import increment, get_lib_modules, ping, startup_check
import functools
import operator
import json
import importlib
import nats

def pytest_addoption(parser):
    parser.addoption('--natscredfile', action='store', default=None)

@pytest.fixture(scope='session')
def nats_server(loop, request):
    nats_cred_file = request.config.getoption('--natscredfile')

    print('Creating NATS fixture')

    if nats_cred_file:
        nats_url = 'tls://connect.ngs.global'
    else:
        nats_url = 'nats://127.0.0.1:4222'
        p = subprocess.Popen(['nats-server', '-D'])
    
    yield nats_url, nats_cred_file
    
    if p:
        p.terminate()
        p.wait()


@pytest.fixture(scope='session')
def nats_client(loop, nats_server):
    (url, cred_file) = nats_server

    client = None

    async def f():
        nonlocal client
        client = await nats.connect(url,  user_credentials=cred_file)

    loop.run_until_complete(f())

    yield client

@pytest.fixture(scope='session', params=get_lib_modules())
def dispatcher_server(loop, nats_server, request, nats_client):
    (nats_url, nats_cred_file) = nats_server
    lib_name = request.param
    test_module_name = 'lib.{}.dispatch'.format(lib_name)
    l = importlib.import_module(test_module_name)

    s: subprocess.Popen = l.start(nats_url, nats_cred_file)

    try:                                
        startup_check(loop, lambda: ping(lib_name), times=20)
    except Exception:
        raise       

    yield s

    async def t2():
        req = json.dumps([{}, {'End': {}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())        

    try:    
        s.wait(timeout=10)
    except subprocess.TimeoutExpired:
        s.terminate()
        s.wait()



# @pytest.fixture(scope='session', autouse=True)
# def event_loop():
#     print('Overriding event loop')
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()
    
@pytest.fixture(scope='session')
def loop():
    l = asyncio.new_event_loop()
    asyncio.set_event_loop(l)
    return l


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if 'test_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in basic_cases for rq, rs in basic_cases[k]])
    elif 'test_binary_client_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in basic_cases for rq, rs in basic_cases[k]], ids=increment())
    elif 'test_client_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in basic_cases for rq, rs in basic_cases[k]], ids=increment())
    elif 'test_binary_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in binary_cases for rq, rs in binary_cases[k]], ids=increment())
    elif 'test_mock_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(k, [[dc(rq), dc(rs)] for rq, rs in mock_cases[k]]) for k in mock_cases])
    elif 'test_mock_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in mock_invalid_cases for rq, rs in mock_invalid_cases[k]], ids=increment())
    elif 'test_schema_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in parse_cases for rq, rs in parse_cases[k]], ids=increment())
    elif 'test_cold_binary_client_server_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(k, [[dc(rq), dc(rs)] for rq, rs in binary_client_rotation_cases[k]]) for k in binary_client_rotation_cases], ids=increment())

