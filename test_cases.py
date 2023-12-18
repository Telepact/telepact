from test.cases import cases
from unittest import TestCase

import importlib
import socket
import os
import time
import subprocess
import json
import pytest

os.listdir

lib_paths = ['lib/{}'.format(f) for f in os.listdir('lib')
             if os.path.isdir('lib/{}'.format(f))]

libs = [(lib_path, '{}/server.fifo'.format(lib_path),
         '{}.startTestServer'.format(lib_path.replace('/', '.'))) for lib_path in lib_paths]


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
                return header['result']
            elif 'throw' in header:
                return None
            else:
                return [{}, {}]


def run_case(runner, fifo_path, data):
    print('testing')
    request = data[0]
    expectedResponse = data[1]

    requestJson = json.dumps(request)

    with open(fifo_path, 'w') as f:
        f.write(requestJson)

    print(' <--| {}'.format(requestJson))

    with open(fifo_path, 'r') as f:
        backdoorRequestJson = f.read()

    print(' >| {}'.format(backdoorRequestJson))

    backdoorRequest = json.loads(backdoorRequestJson)
    backdoorResponse = handler(backdoorRequest)
    backdoorResponseJson = json.dumps(backdoorResponse)

    with open(fifo_path, 'w') as f:
        f.write(backdoorResponseJson)

    print(' <| {}'.format(backdoorRequestJson))

    with open(fifo_path, 'r') as f:
        responseJson = f.read()

    print(' -->| {}'.format(responseJson))

    response = json.loads(responseJson)

    runner.assertEqual(expectedResponse, response)


def get_cases():
    new_cases = []
    for lib_path, fifo_path, mod_name in libs:
        for k, v in cases.items():
            for data in v:
                new_cases.append((fifo_path, data))
    return new_cases


class TestCases(TestCase):

    test_servers = []

    def setUp(self):
        for lib_path, fifo_path, mod_name in libs:

            mod = importlib.import_module(mod_name)

            os.mkfifo(fifo_path)

            print('Starting server in {}'.format(lib_path))
            process = mod.run('../../test/example.japi.json')
            self.test_servers.append((fifo_path, process))

    def tearDown(self):
        for fifo_path, process in self.test_servers:
            os.remove(fifo_path)
            process.terminate()

    # need to figure this out

    @pytest.mark.parametrize('fifo_path,data', get_cases())
    def test_case(self, fifo_path, data):
        run_case(self, fifo_path, data)
