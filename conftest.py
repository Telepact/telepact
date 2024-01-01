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


# @pytest.fixture(scope='session', autouse=True)
# def event_loop():
#     print('Overriding event loop')
#     try:
#         loop = asyncio.get_running_loop()
#     except RuntimeError:
#         loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()