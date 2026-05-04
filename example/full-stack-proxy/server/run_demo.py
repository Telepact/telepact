#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from __future__ import annotations

import argparse
import asyncio
import signal
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import websockets

ROOT = Path(__file__).resolve().parent.parent
SERVER_APP = ROOT / 'server' / 'app.py'
PROXY_APP = ROOT / 'proxy' / 'app.py'


def wait_for_tcp(host: str, port: int, timeout_seconds: float = 10.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            if sock.connect_ex((host, port)) == 0:
                return
        time.sleep(0.1)
    raise TimeoutError(f'timed out waiting for {host}:{port}')


def wait_for_http(url: str, timeout_seconds: float = 10.0) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=0.5) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.1)
    raise TimeoutError(f'timed out waiting for {url}')


def wait_for_websocket(url: str, timeout_seconds: float = 10.0) -> None:
    async def connect_once() -> None:
        async with websockets.connect(url):
            return

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        try:
            asyncio.run(connect_once())
            return
        except Exception:
            time.sleep(0.1)
    raise TimeoutError(f'timed out waiting for {url}')


def terminate_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=5)


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the full-stack proxy demo stack.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=4173)
    parser.add_argument('--proxy-port', type=int, default=4174)
    parser.add_argument('--nats-port', type=int, default=42223)
    parser.add_argument('--topic', default='example.full-stack-proxy.telepact')
    args = parser.parse_args()

    nats_url = f'nats://{args.host}:{args.nats_port}'
    processes: list[subprocess.Popen[bytes]] = []

    def shutdown(*_args: object) -> None:
        for process in reversed(processes):
            terminate_process(process)
        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    nats_process = subprocess.Popen([
        'nats-server',
        '-a', args.host,
        '-p', str(args.nats_port),
    ])
    processes.append(nats_process)
    wait_for_tcp(args.host, args.nats_port)

    proxy_process = subprocess.Popen([
        sys.executable,
        str(PROXY_APP),
        '--host', args.host,
        '--port', str(args.proxy_port),
        '--nats-url', nats_url,
    ])
    processes.append(proxy_process)
    wait_for_websocket(f'ws://{args.host}:{args.proxy_port}/ws/telepact?topic=healthcheck')

    server_process = subprocess.Popen([
        sys.executable,
        str(SERVER_APP),
        '--host', args.host,
        '--port', str(args.port),
        '--nats-url', nats_url,
        '--topic', args.topic,
    ])
    processes.append(server_process)
    wait_for_http(f'http://{args.host}:{args.port}/healthz')

    while True:
        for process in processes:
            return_code = process.poll()
            if return_code is not None:
                for other_process in reversed(processes):
                    if other_process is not process:
                        terminate_process(other_process)
                raise SystemExit(return_code)
        time.sleep(0.2)


if __name__ == '__main__':
    main()
