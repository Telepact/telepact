import sys
import subprocess


def run(schemaFileName):
    return subprocess.run(['mvn', 'test-compile', 'exec:java', '-Dexec.classpathScope=test', '-Dexec.mainClass=io.github.brenbar.japi.TestServer',
                           '-Dexec.args={}'.format(schemaFileName)])
