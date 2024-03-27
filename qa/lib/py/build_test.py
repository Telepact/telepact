import subprocess
import pathlib
import os

this_path = pathlib.Path(__file__).parent.resolve()
target_path = os.path.join(pathlib.Path(
    __file__).parent.parent.parent.parent.resolve(), './lib/py')
this_env = os.environ.copy()


def start(nats_url):
    this_env['NATS_URL'] = nats_url
    this_env['PYTHONTRACEMALLOC'] = '1'

    s0 = subprocess.Popen(['pipenv', 'uninstall', 'uapi'], cwd=this_path)
    s0.wait()

    s1 = subprocess.Popen(['pipenv', '--clear'], cwd=this_path)
    s1.wait()

    s3 = subprocess.Popen(['pipenv', 'run', 'python',
                           'prepare.py'], cwd=target_path)
    s3.wait()

    s = subprocess.Popen(['pipenv', 'run', 'python',
                         '-m', 'build'], cwd=target_path)
    s.wait()

    s2 = subprocess.Popen(
        ['pipenv', 'install', './../../../lib/py/dist/uapi-0.0.1-py3-none-any.whl', '--clear'], cwd=this_path)
    s2.wait()

    p = subprocess.Popen(['pipenv', 'run', 'python',
                         '-m', 'uapitest'], cwd=this_path, env=this_env)

    return p
