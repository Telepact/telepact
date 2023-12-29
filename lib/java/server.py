import sys
import subprocess
import pathlib

this_path = pathlib.Path(__file__).parent.resolve()


def start(api_schema_path, nats_url, frontdoor_topic, backdoor_topic):
    return subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.TestServer',
                             '-Dexec.args="{} {} {} {}"'.format(api_schema_path, nats_url, frontdoor_topic, backdoor_topic)], cwd=this_path)
