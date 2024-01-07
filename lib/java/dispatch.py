import subprocess
import pathlib

this_path = pathlib.Path(__file__).parent.resolve()


def start():
    p = subprocess.Popen(['mvn', 'verify'], cwd=this_path)

    return p
