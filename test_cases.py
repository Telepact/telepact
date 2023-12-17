from test.cases import cases
from unittest import TestCase

import importlib
import socket
import os
import time
import subprocess
import json

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


class TestCases(TestCase):
    def test_case(self):
        for lib in libs:
            modName = '{}.startTestServer'.format(lib.replace('/', '.'))
            mod = importlib.import_module(modName)
            print('______________________________ HELLO __________________________')
            print(lib)
            os.chdir(lib)
            try:
                process = mod.run('../../test/example.japi.json')
                socket_address = './testServer.socket'
                client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

                while not os.path.exists(socket_address):
                    time.sleep(0.2)

                client.connect(socket_address)

                for k, v in cases.items():
                    for e in v:
                        with self.subTest(e):
                            print('testing {}'.format(e))
                            request = e[0]
                            expectedResponse = e[1]

                            requestJson = json.dumps(request)

                            client.sendall(requestJson.encode())
                            backdoorRequestJson = client.recv(1024)

                            backdoorRequest = json.loads(backdoorRequestJson)
                            backdoorResponse = handler(backdoorRequest)
                            backdoorResponseJson = json.dumps(backdoorResponse)

                            client.sendall(backdoorResponseJson.encode())
                            responseJson = client.recv(1024)

                            response = json.loads(responseJson)

                            self.assertEqual(expectedResponse, response)
            finally:
                process.terminate()
                os.remove(socket_address)
                os.chdir('../..')
