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

    for _ in range(10):
        print('Checking for server ready')
        try:
            Path('{}/SERVER_READY'.format(this_path)).unlink()
            print('Server is good to go')
            for _ in range(10):
                print('Checking for client server ready')
                try:
                    Path('{}/CLIENT_SERVER_READY'.format(this_path)).unlink()
                    print('Server is good to go')
                    return [p1, p2]
                except FileNotFoundError:
                    time.sleep(1)

        except FileNotFoundError:
            time.sleep(1)

    p1.terminate()
    p1.wait()
    p2.terminate()
    p2.wait()
    raise Exception('Server did not start properly')
