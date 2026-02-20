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
class TransportMessage:
    payload: bytes
    reply_channel: str | None

    _transport: "Transport" = None  # type: ignore[assignment]

    async def respond(self, payload: bytes):
        if self.reply_channel is None:
            raise RuntimeError("message has no reply channel")
        await self._transport.send(self.reply_channel, payload)


@dataclass
class CallResult:
    payload: bytes


class Listener:
    def __init__(self, transport: "Transport", lid: str):
        self._transport = transport
        self._lid = lid
        self._closed = False

    async def close(self, limit: int | None = None):
        # limit is currently ignored by the remote side, but accepted for
        # runner parity.
        _ = limit
        if self._closed:
            return
        self._closed = True
        await self._transport._unlisten(self._lid)


class Transport:
    def __init__(self):
        self._lid_counter = 0
        self._cid_counter = 0
        self._write_lock = asyncio.Lock()

        self._callbacks: dict[str, Callable[[TransportMessage], Awaitable[None]]] = {}
        self._pending_calls: dict[str, asyncio.Future[bytes]] = {}

        self._reader_task: asyncio.Task | None = None

    async def start(self):
        if self._reader_task is None:
            self._reader_task = asyncio.create_task(self._read_loop())

    async def call(self, channel: str, payload: bytes, timeout: float = 5) -> CallResult:
        self._cid_counter += 1
        cid = f"cid-{self._cid_counter}"
        future: asyncio.Future[bytes] = asyncio.get_running_loop().create_future()
        self._pending_calls[cid] = future

        timeout_ms = int(max(timeout, 0.001) * 1000)
        await self._send({
            "op": "call",
            "cid": cid,
            "channel": channel,
            "timeout_ms": timeout_ms,
            "payload": _encode_bytes(payload),
        })

        try:
            response = await asyncio.wait_for(future, timeout=max(timeout, 0.001))
            return CallResult(payload=response)
        except asyncio.TimeoutError:
            raise
        finally:
            self._pending_calls.pop(cid, None)

    async def send(self, channel: str, payload: bytes):
        await self._send({
            "op": "send",
            "channel": channel,
            "reply_channel": None,
            "payload": _encode_bytes(payload),
        })

    async def listen(self, channel: str, cb: Callable[[TransportMessage], Awaitable[None]]) -> Listener:
        self._lid_counter += 1
        lid = f"lid-{self._lid_counter}"
        self._callbacks[lid] = cb
        await self._send({
            "op": "listen",
            "lid": lid,
            "channel": channel,
        })
        return Listener(self, lid)

    async def sync(self):
        # No-op to preserve existing call sites where stdout flush behavior is
        # expected to be explicit.
        return

    async def _unlisten(self, lid: str):
        self._callbacks.pop(lid, None)
        await self._send({
            "op": "unlisten",
            "lid": lid,
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

        if op == "event":
            lid = frame.get("lid")
            cb = self._callbacks.get(lid)
            if cb is None:
                return

            payload_b64 = frame.get("payload")
            if not isinstance(payload_b64, str):
                return

            msg = TransportMessage(
                payload=_decode_bytes(payload_b64),
                reply_channel=frame.get("reply_channel"),
                _transport=self,
            )
            task = asyncio.create_task(cb(msg))
            task.add_done_callback(_ignore_task_error)
            return

        if op == "call_result":
            cid = frame.get("cid")
            future = self._pending_calls.get(cid)
            if future is None or future.done():
                return

            if frame.get("ok", False):
                payload_b64 = frame.get("payload")
                if not isinstance(payload_b64, str):
                    future.set_exception(RuntimeError("missing call response payload"))
                    return
                future.set_result(_decode_bytes(payload_b64))
            else:
                err = frame.get("error", "call failed")
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


async def connect(_url: str) -> Transport:
    transport = Transport()
    await transport.start()
    return transport
