import sys
import subprocess
import pathlib

this_dir = pathlib.Path(__file__).parent.resolve()


def run(schemaFileName):
    return subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.TestServer',
                             '-Dexec.args={}'.format(schemaFileName)], cwd=this_dir)
