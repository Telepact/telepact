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

import asyncio
import base64
import json
import sys
from dataclasses import dataclass
from typing import Any, Awaitable, Callable


PROTO_PREFIX = "@@TPSTDIO@@"


def _encode_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _decode_bytes(data: str) -> bytes:
    return base64.b64decode(data.encode("ascii"))


@dataclass
class Msg:
    data: bytes
    reply: str | None

    async def respond(self, data: bytes):
        if self.reply is None:
            raise RuntimeError("message has no reply subject")
        await self._connection.publish(self.reply, data)

    _connection: "Client" = None  # type: ignore[assignment]


@dataclass
class RequestResponse:
    data: bytes


class Subscription:
    def __init__(self, connection: "Client", sid: str):
        self._connection = connection
        self._sid = sid
        self._drained = False

    async def drain(self):
        if self._drained:
            return
        self._drained = True
        await self._connection._unsubscribe(self._sid)

    async def unsubscribe(self, limit: int | None = None):
        # limit is accepted for API compatibility, but stdio harness only
        # uses explicit drain/unsubscribe behavior.
        _ = limit
        await self.drain()


class Client:
    def __init__(self):
        self._sid_counter = 0
        self._rid_counter = 0
        self._write_lock = asyncio.Lock()

        self._callbacks: dict[str, Callable[[Msg], Awaitable[None]]] = {}
        self._pending_requests: dict[str, asyncio.Future[bytes]] = {}

        self._reader_task: asyncio.Task | None = None

    async def start(self):
        if self._reader_task is None:
            self._reader_task = asyncio.create_task(self._read_loop())

    async def request(self, subject: str, data: bytes, timeout: float = 5) -> RequestResponse:
        self._rid_counter += 1
        rid = f"rid-{self._rid_counter}"
        future: asyncio.Future[bytes] = asyncio.get_running_loop().create_future()
        self._pending_requests[rid] = future

        timeout_ms = int(max(timeout, 0.001) * 1000)
        await self._send({
            "op": "request",
            "rid": rid,
            "subject": subject,
            "timeout_ms": timeout_ms,
            "data": _encode_bytes(data),
        })

        try:
            response = await asyncio.wait_for(future, timeout=max(timeout, 0.001))
            return RequestResponse(data=response)
        except asyncio.TimeoutError:
            raise
        finally:
            self._pending_requests.pop(rid, None)

    async def publish(self, subject: str, data: bytes):
        await self._send({
            "op": "publish",
            "subject": subject,
            "reply": None,
            "data": _encode_bytes(data),
        })

    async def subscribe(self, subject: str, cb: Callable[[Msg], Awaitable[None]]) -> Subscription:
        self._sid_counter += 1
        sid = f"sid-{self._sid_counter}"
        self._callbacks[sid] = cb
        await self._send({
            "op": "subscribe",
            "sid": sid,
            "subject": subject,
        })
        return Subscription(self, sid)

    async def flush(self):
        # No-op to preserve API compatibility with nats-py.
        return

    async def _unsubscribe(self, sid: str):
        self._callbacks.pop(sid, None)
        await self._send({
            "op": "unsubscribe",
            "sid": sid,
        })

    async def _send(self, payload: dict[str, Any]):
        wire = f"{PROTO_PREFIX}{json.dumps(payload, separators=(',', ':'))}\n"
        async with self._write_lock:
            sys.stdout.write(wire)
            sys.stdout.flush()

    async def _read_loop(self):
        while True:
            line = await asyncio.to_thread(sys.stdin.readline)
            if not line:
                return

            if not line.startswith(PROTO_PREFIX):
                continue

            try:
                frame = json.loads(line[len(PROTO_PREFIX):])
                await self._handle_frame(frame)
            except Exception:
                continue

    async def _handle_frame(self, frame: dict[str, Any]):
        op = frame.get("op")
        if op == "message":
            sid = frame["sid"]
            cb = self._callbacks.get(sid)
            if cb is None:
                return

            msg = Msg(
                data=_decode_bytes(frame["data"]),
                reply=frame.get("reply"),
                _connection=self,
            )
            task = asyncio.create_task(cb(msg))
            task.add_done_callback(_ignore_task_error)
            return

        if op == "request_result":
            rid = frame["rid"]
            future = self._pending_requests.get(rid)
            if future is None or future.done():
                return

            if frame.get("ok", False):
                future.set_result(_decode_bytes(frame["data"]))
            else:
                err = frame.get("error", "request failed")
                if err == "timeout":
                    future.set_exception(asyncio.TimeoutError())
                else:
                    future.set_exception(RuntimeError(err))
            return

        raise RuntimeError(f"unsupported op: {op}")


def _ignore_task_error(task: asyncio.Task):
    try:
        task.result()
    except Exception:
        pass


async def connect(_url: str) -> Client:
    c = Client()
    await c.start()
    return c
