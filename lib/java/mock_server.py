import sys
import subprocess
import pathlib
from pathlib import Path
import time

this_path = pathlib.Path(__file__).parent.resolve()


def start(api_schema_path, nats_url, frontdoor_topic):
    p = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.MockTestServer',
                          '-Dexec.args="{} {} {}"'.format(api_schema_path, nats_url, frontdoor_topic)], cwd=this_path)

    for _ in range(10):
        print('Checking for server ready')
        try:
            Path('{}/MOCK_SERVER_READY'.format(this_path)).unlink()
            print('Server is good to go')
            return p
        except FileNotFoundError:
            time.sleep(1)

    p.terminate()
    p.wait()
    raise Exception('Server did not start properly')
