import sys
import subprocess
import pathlib

this_path = pathlib.Path(__file__).parent.resolve()


def start(schemaFileName):
    p1 = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.TestServer',
                           '-Dexec.args={}'.format(schemaFileName)], cwd=this_path)
    p2 = subprocess.Popen(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test',
                          '-Dexec.mainClass=io.github.brenbar.japi.ClientTestServer'], cwd=this_path)
    return [p1, p2]
