import subprocess
import pathlib
import os

this_path = pathlib.Path(__file__).parent.resolve()
target_path = os.path.join(pathlib.Path(
    __file__).parent.parent.parent.parent.resolve(), './lib/py')
other_target_path = os.path.join(pathlib.Path(
    __file__).parent.parent.parent.parent.resolve(), './tool/uapicodegen')
this_env = os.environ.copy()


def start(nats_url):
    this_env['NATS_URL'] = nats_url
    this_env['PYTHONTRACEMALLOC'] = '1'
    del this_env["VIRTUAL_ENV"]

    p2 = subprocess.Popen(['make'], cwd=this_path, env=this_env)
    p2.wait()

    p = subprocess.Popen(['poetry', 'run', 'python',
                         '-m', 'uapitest'], cwd=this_path, env=this_env)

    return p
