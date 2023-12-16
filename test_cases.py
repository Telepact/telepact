from test.cases import cases
from unittest import TestCase

import importlib
import socket
import os
import time
import subprocess

os.listdir

libs = ['lib/{}'.format(f) for f in os.listdir('lib')
        if os.path.isdir('lib/{}'.format(f))]


class TestCases(TestCase):
    def test_case(self):
        for lib in libs:
            modName = '{}.startTestServer'.format(lib.replace('/', '.'))
            mod = importlib.import_module(modName)
            os.chdir(lib)
            process = mod.run('../../test/example.japi.json')
            for k, v in cases.items():
                with self.subTest(v):
                    print('testing')
                    request = v[0]
                    expectedResponse = v[1]
                    actualResponse = []
                    self.assertEqual(expectedResponse, actualResponse)
