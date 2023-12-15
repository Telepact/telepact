import sys
import subprocess

schemaFileName = sys.argv[1]

subprocess.run(['mvn', 'exec:java', '-Dexec.mainClass=io.github.brenbar.japi.TestServer"',
               '-Dexec.args={}'.format(schemaFileName)])
