import subprocess
import pathlib
import os

this_path = pathlib.Path(__file__).parent.resolve()
target_path = os.path.join(pathlib.Path(__file__).parent.parent.parent.parent.resolve(), './lib/java')
this_env = os.environ.copy()


def start(nats_url):
    this_env['NATS_URL'] = nats_url

    s = subprocess.Popen(['mvn', 'install'], cwd=target_path)
    s.wait()
    p = subprocess.Popen(['mvn', 'verify'], cwd=this_path, env=this_env)

    return p
