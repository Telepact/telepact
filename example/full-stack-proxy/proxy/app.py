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
import logging
from http.cookies import SimpleCookie
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

import nats
import websockets

REQUEST_ID_HEADER = 'x-telepact-request-id'
SESSION_HEADER = 'x-telepact-session'
REQUEST_TIMEOUT_SECONDS = 10

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger('telepact.example.full_stack_proxy.proxy')


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


async def proxy_connection(websocket: websockets.ServerConnection, connection: nats.aio.client.Client) -> None:
    request = getattr(websocket, 'request', None)
    request_path = getattr(request, 'path', '/ws/telepact')
    parsed = urlsplit(request_path)
    if parsed.path != '/ws/telepact':
        await websocket.close(code=1008, reason='unexpected path')
        return

    query = parse_qs(parsed.query)
    topic = query.get('topic', [''])[0]
    if topic == '':
        await websocket.close(code=1008, reason='missing topic')
        return

    headers = getattr(request, 'headers', None)
    cookie_header = None if headers is None else headers.get('Cookie')
    session_token = read_session_cookie(cookie_header)

    async for request_bytes in websocket:
        request_payload = request_bytes.encode('utf-8') if isinstance(request_bytes, str) else bytes(request_bytes)
        transport_headers = {REQUEST_ID_HEADER: str(uuid4())}
        if session_token is not None:
            transport_headers[SESSION_HEADER] = session_token
        response = await connection.request(
            topic,
            request_payload,
            timeout=REQUEST_TIMEOUT_SECONDS,
            headers=transport_headers,
        )
        await websocket.send(response.data)


async def main_async(host: str, port: int, nats_url: str) -> None:
    connection = await nats.connect(nats_url)
    log.info('serving websocket proxy on ws://%s:%s/ws/telepact', host, port)
    try:
        async with websockets.serve(
            lambda websocket: proxy_connection(websocket, connection),
            host,
            port,
        ):
            await asyncio.Future()
    finally:
        await connection.drain()


def main() -> None:
    parser = argparse.ArgumentParser(description='Run the full-stack websocket-to-NATS proxy.')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8001)
    parser.add_argument('--nats-url', default='nats://127.0.0.1:4222')
    args = parser.parse_args()
    asyncio.run(main_async(args.host, args.port, args.nats_url))


if __name__ == '__main__':
    main()
