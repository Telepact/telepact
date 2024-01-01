import sys
import subprocess
import pathlib
import time
from pathlib import Path

this_path = pathlib.Path(__file__).parent.resolve()


def start(api_schema_path, nats_url, client_frontdoor_topic, client_backdoor_topic, frontdoor_topic, backdoor_topic):
    print('STARTING client server')
    p1 = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.TestServer',
                           '-Dexec.args="{},{},{},{}"'.format(api_schema_path, nats_url, frontdoor_topic, backdoor_topic)], cwd=this_path)
    p2 = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test',
                          '-Dexec.mainClass=io.github.brenbar.japi.ClientTestServer', '-Dexec.args="{},{},{}"'.format(nats_url, client_frontdoor_topic, client_backdoor_topic)], cwd=this_path)

    return [p1, p2]
