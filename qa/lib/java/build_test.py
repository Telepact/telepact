import subprocess
import pathlib
import os

this_path = pathlib.Path(__file__).parent.resolve()
this_env = os.environ.copy()


def start(nats_url):
    this_env['NATS_URL'] = nats_url

    p = subprocess.Popen(['mvn', 'compile', 'exec:java',
                         '-Dexec.mainClass=uapitest.Main'], cwd=this_path, env=this_env)

    return p
