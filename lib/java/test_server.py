import sys
import subprocess
import pathlib
import time
import signal
from pathlib import Path

this_path = pathlib.Path(__file__).parent.resolve()


def start_basic_server(api_schema_path: str, nats_url: str, frontdoor_topic: str, backdoor_topic: str) -> subprocess.Popen:
    argString = '-Dexec.args="{},{},{},{}"'.format(
        api_schema_path, nats_url, frontdoor_topic, backdoor_topic)
    print(argString)
    p = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.TestServer',
                          argString], cwd=this_path)

    return p


def start_schema_server(api_schema_path: str, nats_url: str, frontdoor_topic: str) -> subprocess.Popen:
    p = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.SchemaTestServer',
                          '-Dexec.args="{},{},{}"'.format(api_schema_path, nats_url, frontdoor_topic)], cwd=this_path)

    return p


def start_mock_server(api_schema_path: str, nats_url: str, frontdoor_topic: str) -> subprocess.Popen:
    p = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.MockTestServer',
                          '-Dexec.args="{},{},{}"'.format(api_schema_path, nats_url, frontdoor_topic)], cwd=this_path)

    return p


def start_client_server(api_schema_path: str, nats_url: str, client_frontdoor_topic: str, client_backdoor_topic: str, frontdoor_topic, backdoor_topic: str) -> list[subprocess.Popen]:
    print('STARTING client server')
    p1 = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.TestServer',
                           '-Dexec.args="{},{},{},{}"'.format(api_schema_path, nats_url, frontdoor_topic, backdoor_topic)], cwd=this_path)
    p2 = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test',
                          '-Dexec.mainClass=io.github.brenbar.japi.ClientTestServer', '-Dexec.args="{},{},{}"'.format(nats_url, client_frontdoor_topic, client_backdoor_topic)], cwd=this_path)

    return [p1, p2]
