import subprocess
import pytest
import asyncio

@pytest.fixture(scope='session')
def nats_server():
    print('Creating NATS fixture')
    p = subprocess.Popen(['nats-server', '-DV'])
    yield p
    p.terminate()
    p.wait()

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()

    yield loop

    pending = asyncio.tasks.all_tasks(loop)
    loop.run_until_complete(asyncio.gather(*pending))
    loop.run_until_complete(asyncio.sleep(1))

    loop.close()