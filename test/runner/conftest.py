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
from parameters.api_examples_cases import auth_cases as api_examples_auth_cases
from parameters.api_examples_cases import mock_cases as api_examples_mock_cases
from parameters.auth_cases import cases as auth_cases
from parameters.binary_cases import cases as binary_cases
from parameters.binary_cases import binary_client_rotation_cases
from parameters.cases import cases as basic_cases
from parameters.garbage_cases import cases as garbage_cases
from parameters.mock_cases import cases as mock_cases
from parameters.mock_cases import invalid_cases as mock_invalid_cases
from parameters.mockgen_cases import cases as mockgen_cases
from parameters.parse_cases import cases as parse_cases
from parameters.test_client_cases import cases as test_client_cases
from util import increment, ping, startup_check
import json
import nats
import os


NATS_TIMEOUT_RETRIES = 1
NATS_TIMEOUT_RETRY_DELAY_SECONDS = 0.25
NATS_TIMEOUT_RETRY_MAX_SECONDS = 5


class RetryingNatsClient:
    def __init__(self, client):
        self._client = client

    async def request(self, *args, **kwargs):
        timeout = kwargs.get('timeout')
        if timeout is None and len(args) >= 3:
            timeout = args[2]

        retries = NATS_TIMEOUT_RETRIES if timeout and timeout <= NATS_TIMEOUT_RETRY_MAX_SECONDS else 0
        subject = kwargs.get('subject', args[0] if args else '<unknown>')

        for attempt in range(retries + 1):
            try:
                return await self._client.request(*args, **kwargs)
            except nats.errors.TimeoutError:
                if attempt >= retries:
                    raise

                print(
                    'NATS timeout for {}. Retrying {}/{}...'.format(
                        subject,
                        attempt + 1,
                        retries,
                    ),
                    flush=True,
                )
                await asyncio.sleep(NATS_TIMEOUT_RETRY_DELAY_SECONDS)

    def __getattr__(self, attr):
        return getattr(self._client, attr)


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
    parser.addoption('--remotenats', action='store', default=None)


@pytest.fixture(scope='session')
def nats_server(loop, request):
    remote_nats = request.config.getoption('--remotenats')

    print('Creating NATS fixture')

    p = None
    if remote_nats:
        print('###########################################################################')
        print('#                                WARNING!                                 #')
        print('#                                                                         #')
        print('#                        Using remote NATS server                         #')
        print('###########################################################################')
        print('')
        nats_url = 'nats://demo.nats.io:4222'
    else:
        nats_url = 'nats://127.0.0.1:4222'
        p = subprocess.Popen(['nats-server', '-D'])

    yield nats_url

    if p:
        p.terminate()
        p.wait()


@pytest.fixture(scope='session')
def nats_client(loop, nats_server):
    url = nats_server

    client = None

    async def f():
        nonlocal client
        print('NATS client connecting to {}'.format(url))
        client = await nats.connect(url)

    loop.run_until_complete(f())

    print('NATS client connected!')

    yield RetryingNatsClient(client)


@pytest.fixture(scope='session', params=get_lib_modules())
def dispatcher_server(loop, nats_server, request, nats_client):
    nats_url = nats_server
    lib_name = request.param

    env_vars = os.environ.copy()
    del env_vars['VIRTUAL_ENV']
    env_vars['NATS_URL'] = nats_url

    path = '../lib/' + lib_name
    s = subprocess.Popen(['make', 'test-server'], cwd=path, env=env_vars)

    try:
        startup_check(loop, lambda: ping(nats_client, lib_name), times=30)
    except Exception:
        raise

    yield lib_name

    async def t2():
        req = json.dumps([{}, {'End': {}}])
        await nats_client.request(lib_name, req.encode(), timeout=1)

    loop.run_until_complete(t2())

    try:
        s.wait(timeout=20)
    except subprocess.TimeoutExpired:
        s.terminate()
        s.wait()


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
    elif 'test_api_examples_auth_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [
                             (k, rq, rs) for k in api_examples_auth_cases for rq, rs in api_examples_auth_cases[k]], ids=increment())
    elif 'test_api_examples_mock_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [
                             (k, rq, rs) for k in api_examples_mock_cases for rq, rs in api_examples_mock_cases[k]], ids=increment())
    elif 'test_cold_binary_client_server_multi_case' == metafunc.function.__name__:
        metafunc.parametrize('name,statements', [(
            k, [[rq, rs] for rq, rs in binary_client_rotation_cases[k]]) for k in binary_client_rotation_cases], ids=increment())
    elif 'test_garbage_case' == metafunc.function.__name__:
        metafunc.parametrize('name,req,res', [(
            k, rq, rs) for k in garbage_cases for rq, rs in garbage_cases[k]], ids=increment())
