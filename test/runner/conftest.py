#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

import subprocess
import pytest
import asyncio
from cases import cases as basic_cases
from binary_cases import cases as binary_cases
from binary_cases import binary_client_rotation_cases
from mock_cases import cases as mock_cases
from mock_cases import invalid_cases as mock_invalid_cases
from mockgen_cases import cases as mockgen_cases
from parse_cases import cases as parse_cases
from garbage_cases import cases as garbage_cases
from auth_cases import cases as auth_cases
from test_client_cases import cases as test_client_cases
from util import increment, ping, startup_check
from stdio_bus import StdioBus
import json
import os

def pytest_runtest_makereport(item, call):
    if call.excinfo is not None and call.excinfo.typename not in ("AssertionError", "Skipped"):
        print(f"Error: {call.excinfo.value}")
        print(f"Type: {call.excinfo.typename}")
        print(f"Traceback: {call.excinfo.traceback}")
        item.session.shouldstop = "Skipping all future tests due to an error."

def get_lib_modules():
    result = [f for f in os.listdir('../../lib')
              if os.path.isdir('../../lib/{}'.format(f))]
    return result


def pytest_addoption(parser):
    parser.addoption('--remote-transport', action='store', default=None)


@pytest.fixture(scope='session')
def transport_url(loop, request):
    remote_transport = request.config.getoption('--remote-transport')
    if remote_transport:
        print('Ignoring --remote-transport: test harness now uses stdio transport.')

    print('Creating stdio transport fixture')
    yield 'stdio://local'


@pytest.fixture(scope='session')
def stdio_bus(loop):
    bus = StdioBus(loop)
    yield bus
    loop.run_until_complete(bus.close())


@pytest.fixture(scope='session')
def transport_client(stdio_bus):
    print('stdio client connected!')
    yield stdio_bus.client()


@pytest.fixture(scope='session', params=get_lib_modules())
def dispatcher_server(loop, transport_url, request, transport_client, stdio_bus):
    lib_name = request.param

    env_vars = os.environ.copy()
    env_vars.pop('VIRTUAL_ENV', None)
    env_vars['TP_TRANSPORT_URL'] = transport_url

    path = '../lib/' + lib_name
    s = subprocess.Popen(
        ['make', 'test-server'],
        cwd=path,
        env=env_vars,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    stdio_bus.attach_process(lib_name, s)

    try:
        startup_check(loop, lambda: ping(transport_client, lib_name), times=30)
    except Exception:
        stdio_bus.detach_process(lib_name)
        s.terminate()
        s.wait()
        raise

    yield lib_name

    async def t2():
        req = json.dumps([{}, {'End': {}}])
        await transport_client.call(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())

    try:
        s.wait(timeout=20)
    except subprocess.TimeoutExpired:
        s.terminate()
        s.wait()
    finally:
        stdio_bus.detach_process(lib_name)


@pytest.fixture(scope='session')
def loop():
    l = asyncio.new_event_loop()
    asyncio.set_event_loop(l)
    return l


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if 'test_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [
                             (k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]])
    elif 'test_binary_client_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]], ids=increment())
    elif 'test_pbinary_client_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]], ids=increment())
    elif 'test_client_server_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]], ids=increment())
    elif 'test_client_server_codegen_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in basic_cases for rq, rs in basic_cases[k]], ids=increment())
    elif 'test_binary_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in binary_cases for rq, rs in binary_cases[k]], ids=increment())
    elif 'test_mock_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [
                             (k, [[rq, rs] for rq, rs in mock_cases[k]]) for k in mock_cases])
    elif 'test_mockgen_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [
                             (k, [[rq, rs] for rq, rs in mockgen_cases[k]]) for k in mockgen_cases])
    elif 'test_mock_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in mock_invalid_cases for rq, rs in mock_invalid_cases[k]], ids=increment())
    elif 'test_test_client_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [
                             (k, [[rq, rs] for rq, rs in test_client_cases[k]]) for k in test_client_cases])
    elif 'test_schema_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in parse_cases for rq, rs in parse_cases[k]], ids=increment())
    elif 'test_auth_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [
                             (k, rq, rs) for k in auth_cases for rq, rs in auth_cases[k]], ids=increment())
    elif 'test_cold_binary_client_server_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(
            k, [[rq, rs] for rq, rs in binary_client_rotation_cases[k]]) for k in binary_client_rotation_cases], ids=increment())
    elif 'test_garbage_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in garbage_cases for rq, rs in garbage_cases[k]], ids=increment())
