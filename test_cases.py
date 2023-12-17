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

libs = ['lib/{}'.format(f) for f in os.listdir('lib')
        if os.path.isdir('lib/{}'.format(f))]


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


def run_case(runner, socket_path, e):
    print('testing')
    request = e[0]
    expectedResponse = e[1]

    requestJson = json.dumps(request)

    with open(socket_path, 'w') as f:
        f.write(requestJson)

    print(' <--| {}'.format(requestJson))

    with open(socket_path, 'r') as f:
        backdoorRequestJson = f.read()

    print(' >| {}'.format(backdoorRequestJson))

    backdoorRequest = json.loads(backdoorRequestJson)
    backdoorResponse = handler(backdoorRequest)
    backdoorResponseJson = json.dumps(backdoorResponse)

    with open(socket_path, 'w') as f:
        f.write(backdoorResponseJson)

    print(' <| {}'.format(backdoorRequestJson))

    with open(socket_path, 'r') as f:
        responseJson = f.read()

    print(' -->| {}'.format(responseJson))

    response = json.loads(responseJson)

    runner.assertEqual(expectedResponse, response)


class TestCases(TestCase):

    # need to figure this out
    @pytest.mark.parametrize()
    def test_case(self):
        for lib in libs:
            modName = '{}.startTestServer'.format(lib.replace('/', '.'))
            mod = importlib.import_module(modName)
            print('______________________________ HELLO __________________________')
            print(lib)
            os.chdir(lib)
            try:
                process = mod.run('../../test/example.japi.json')
                socket_path = './testServer.socket'

                os.mkfifo(socket_path)

                run_case(self, socket_path, next(iter(cases.values()))[0])
                # for k, v in cases.items():
                #     for e in v:
                #         with self.subTest(e):
                #             run_case(self, socket_path, e)
            finally:
                process.terminate()
                os.remove(socket_path)
                os.chdir('../..')
