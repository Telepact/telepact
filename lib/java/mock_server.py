import sys
import subprocess
import pathlib

this_path = pathlib.Path(__file__).parent.resolve()


def start(schemaFileName):
    return subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.MockTestServer',
                             '-Dexec.args={}'.format(schemaFileName)], cwd=this_path)
