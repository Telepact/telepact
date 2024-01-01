import sys
import subprocess
import pathlib
from pathlib import Path
import time
this_path = pathlib.Path(__file__).parent.resolve()


def start(api_schema_path, nats_url, frontdoor_topic):
    p = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.SchemaTestServer',
                          '-Dexec.args="{},{},{}"'.format(api_schema_path, nats_url, frontdoor_topic)], cwd=this_path)

    return p
