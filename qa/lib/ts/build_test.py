import subprocess
import pathlib
import os

this_path = pathlib.Path(__file__).parent.resolve()
target_path = os.path.join(pathlib.Path(
    __file__).parent.parent.parent.parent.resolve(), './lib/ts')

this_env = os.environ.copy()


def start(nats_url):
    this_env['NATS_URL'] = nats_url

    s1 = subprocess.Popen(['npm', 'uninstall', 'uapi'], cwd=this_path)
    s1.wait()

    s = subprocess.Popen(['npm', 'run', 'build'], cwd=target_path)
    s.wait()

    s2 = subprocess.Popen(['npm', 'install', '--no-save',
                          './../../../lib/ts/uapi-1.0.2.tgz'], cwd=this_path)
    s2.wait()

    s3 = subprocess.Popen(['npm', 'run', 'build'], cwd=this_path)
    s3.wait()

    p = subprocess.Popen(['npm', 'start'], cwd=this_path, env=this_env)

    return p
