import subprocess
import pytest

@pytest.fixture(scope='session')
def nats_server():
    print('Creating NATS fixture')
    p = subprocess.Popen(['nats-server', '-DV'])
    yield p
    p.terminate()
    p.wait()