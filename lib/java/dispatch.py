import subprocess
import pathlib

this_path = pathlib.Path(__file__).parent.resolve()


def start(nats_url, cred_file):
    p = subprocess.Popen(['mvn', 'verify'], cwd=this_path, env={
                         'NATS_URL': nats_url, 'NATS_CRED_FILE': '../../{}'.format(cred_file)})

    return p
