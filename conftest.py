import subprocess
import pytest
import asyncio
from test.cases import cases as basic_cases
from test.invalid_binary_cases import cases as binary_cases
from test.invalid_binary_cases import binary_client_rotation_cases
from test.mock_cases import cases as mock_cases
from test.mock_invalid_stub_cases import cases as mock_invalid_stub_cases
from test.parse_cases import cases as parse_cases

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
    if 'test_basic_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,expected_response', [(k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]])
    elif 'test_binary_client_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,expected_response', [(k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]])
    elif 'test_client_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,expected_response', [(k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]])
    elif 'test_binary_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,expected_response', [(k, rq, rs) for k in binary_cases for rq, rs in binary_cases[k]])
    elif 'test_mock_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(k, s) for k,s in mock_cases.items()])
    elif 'test_mock_invalid_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,expected_response', [(k, rq, rs) for k in mock_invalid_stub_cases for rq, rs in mock_invalid_stub_cases[k]])
    elif 'test_schema_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,expected_response', [(k, rq, rs) for k in parse_cases for rq, rs in parse_cases[k]])
    elif 'test_rotate_binary_client_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(k, s) for k,s in binary_client_rotation_cases.items()])

