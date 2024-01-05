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

@pytest.fixture(scope='session')
def nats_server():
    print('Creating NATS fixture')
    p = subprocess.Popen(['nats-server', '-DV'])
    yield p
    p.terminate()
    p.wait()


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
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in basic_cases for rq, rs in basic_cases[k]])
    elif 'test_client_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in basic_cases for rq, rs in basic_cases[k]])
    elif 'test_binary_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in binary_cases for rq, rs in binary_cases[k]])
    elif 'test_mock_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(k, [[dc(rq), dc(rs)] for rq, rs in mock_cases[k]]) for k in mock_cases])
    elif 'test_mock_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in mock_invalid_cases for rq, rs in mock_invalid_cases[k]])
    elif 'test_schema_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(k, dc(rq), dc(rs)) for k in parse_cases for rq, rs in parse_cases[k]])
    elif 'test_cold_binary_client_server_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(k, [[dc(rq), dc(rs)] for rq, rs in binary_client_rotation_cases[k]]) for k in binary_client_rotation_cases])

