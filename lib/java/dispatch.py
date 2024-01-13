import subprocess
import pathlib
import os

this_path = pathlib.Path(__file__).parent.resolve()
this_env = os.environ.copy()


def start(nats_url, cred_file):
    this_env['NATS_URL'] = nats_url
    this_env['NATS_CRED_FILE'] = '../../{}'.format(cred_file)
    p = subprocess.Popen(['mvn', 'verify'], cwd=this_path, env=this_env)

    return p
