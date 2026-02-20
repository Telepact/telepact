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
import subprocess
import threading
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
    _client: "RunnerTransportClient" | None = None

    async def respond(self, payload: bytes):
        if self.reply_channel is None:
            raise RuntimeError("message has no reply_channel channel")
        if self._client is None:
            raise RuntimeError("message is detached from transport")
        await self._client.send(self.reply_channel, payload)


@dataclass
class CallResult:
    payload: bytes


@dataclass
class _ListenerState:
    lid: str
    endpoint: str
    channel: str
    callback: Callable[[TransportMessage], Awaitable[None]] | None = None
    remaining_events: int | None = None


class RunnerListener:
    def __init__(self, bus: "StdioBus", lid: str):
        self._bus = bus
        self._lid = lid

    async def close(self, limit: int | None = None):
        await self._bus.close_runner_listener(self._lid, limit=limit)


class RunnerTransportClient:
    def __init__(self, bus: "StdioBus"):
        self._bus = bus

    async def call(self, channel: str, payload: bytes, timeout: float = 1):
        response = await self._bus.call_from_runner(channel, payload, timeout)
        return CallResult(payload=response)

    async def send(self, channel: str, payload: bytes):
        await self._bus.send_from_runner(channel, payload)

    async def listen(self, channel: str, cb: Callable[[TransportMessage], Awaitable[None]]):
        return await self._bus.listen_runner(channel, cb)


class _RemoteEndpoint:
    def __init__(self, name: str, process: subprocess.Popen):
        self.name = name
        self.process = process
        self._write_lock = threading.Lock()

    def send_json(self, payload: dict[str, Any]):
        line = f"{PROTO_PREFIX}{json.dumps(payload, separators=(',', ':'))}\n"
        with self._write_lock:
            if not self.process.stdin or self.process.stdin.closed:
                raise RuntimeError(f"stdin closed for endpoint {self.name}")
            self.process.stdin.write(line)
            self.process.stdin.flush()


class StdioBus:
    def __init__(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop
        self._listener_counter = 0
        self._reply_counter = 0

        self._listeners: dict[str, _ListenerState] = {}
        self._channels_to_lids: dict[str, list[str]] = {}

        self._pending_replies: dict[str, asyncio.Future[bytes]] = {}
        self._remote_endpoints: dict[str, _RemoteEndpoint] = {}
        self._endpoint_lids: dict[str, set[str]] = {}

        self._runner_client = RunnerTransportClient(self)

    def client(self) -> RunnerTransportClient:
        return self._runner_client

    async def close(self):
        # No-op: fixture teardown owns child process lifecycle.
        return

    async def listen_runner(self, channel: str, cb: Callable[[TransportMessage], Awaitable[None]]):
        self._listener_counter += 1
        lid = f"runner-{self._listener_counter}"
        state = _ListenerState(
            lid=lid,
            endpoint="runner",
            channel=channel,
            callback=cb,
        )
        self._register_listener(state)
        return RunnerListener(self, lid)

    async def close_runner_listener(self, lid: str, limit: int | None = None):
        state = self._listeners.get(lid)
        if not state or state.endpoint != "runner":
            return

        if limit is None or limit <= 0:
            self._remove_listener(lid)
            return

        state.remaining_events = limit

    async def call_from_runner(self, channel: str, payload: bytes, timeout_s: float):
        return await self._call("runner", channel, payload, timeout_s)

    async def send_from_runner(self, channel: str, payload: bytes):
        await self._send("runner", channel, payload, reply_channel=None)

    def attach_process(self, endpoint_name: str, process: subprocess.Popen):
        endpoint = _RemoteEndpoint(endpoint_name, process)
        self._remote_endpoints[endpoint_name] = endpoint
        self._endpoint_lids.setdefault(endpoint_name, set())

        def stdout_reader():
            try:
                if not process.stdout:
                    return
                for line in process.stdout:
                    if not line:
                        break
                    if line.startswith(PROTO_PREFIX):
                        frame = json.loads(line[len(PROTO_PREFIX):])
                        fut = asyncio.run_coroutine_threadsafe(
                            self._handle_remote_frame(endpoint_name, frame),
                            self.loop,
                        )
                        fut.add_done_callback(
                            lambda f, ep=endpoint_name: _log_threadsafe_future(f, ep)
                        )
                    else:
                        print(line, end="", flush=True)
            except Exception as e:
                print(f"[stdio-bus] stdout reader stopped for {endpoint_name}: {e}", flush=True)

        def stderr_reader():
            try:
                if not process.stderr:
                    return
                for line in process.stderr:
                    if not line:
                        break
                    print(line, end="", flush=True)
            except Exception as e:
                print(f"[stdio-bus] stderr reader stopped for {endpoint_name}: {e}", flush=True)

        threading.Thread(target=stdout_reader, daemon=True).start()
        threading.Thread(target=stderr_reader, daemon=True).start()

    def detach_process(self, endpoint_name: str):
        self._remove_endpoint(endpoint_name)

    async def _handle_remote_frame(self, endpoint_name: str, frame: dict[str, Any]):
        op = frame.get("op")

        if op == "listen":
            lid = frame.get("lid")
            channel = frame.get("channel")
            if not isinstance(lid, str) or not isinstance(channel, str):
                raise RuntimeError("invalid listen frame")
            state = _ListenerState(
                lid=lid,
                endpoint=endpoint_name,
                channel=channel,
                callback=None,
            )
            self._register_listener(state)
            self._endpoint_lids.setdefault(endpoint_name, set()).add(lid)
            return

        if op == "unlisten":
            lid = frame.get("lid")
            if not isinstance(lid, str):
                raise RuntimeError("invalid unlisten frame")
            self._remove_listener(lid)
            self._endpoint_lids.setdefault(endpoint_name, set()).discard(lid)
            return

        if op == "send":
            channel = frame.get("channel")
            payload_b64 = frame.get("payload")
            reply_channel = frame.get("reply_channel")
            if not isinstance(channel, str) or not isinstance(payload_b64, str):
                raise RuntimeError("invalid send frame")
            payload = _decode_bytes(payload_b64)
            await self._send(endpoint_name, channel, payload, reply_channel=reply_channel)
            return

        if op == "call":
            cid = frame.get("cid")
            channel = frame.get("channel")
            payload_b64 = frame.get("payload")
            timeout_ms = int(frame.get("timeout_ms", 5000))
            endpoint = self._remote_endpoints.get(endpoint_name)
            if endpoint is None:
                return
            if not isinstance(cid, str) or not isinstance(channel, str) or not isinstance(payload_b64, str):
                raise RuntimeError("invalid call frame")

            payload = _decode_bytes(payload_b64)

            try:
                response_bytes = await self._call(
                    endpoint_name,
                    channel,
                    payload,
                    timeout_s=max(timeout_ms, 1) / 1000.0,
                )
                endpoint.send_json({
                    "op": "call_result",
                    "cid": cid,
                    "ok": True,
                    "payload": _encode_bytes(response_bytes),
                })
            except asyncio.TimeoutError:
                endpoint.send_json({
                    "op": "call_result",
                    "cid": cid,
                    "ok": False,
                    "error": "timeout",
                })
            except Exception as e:
                endpoint.send_json({
                    "op": "call_result",
                    "cid": cid,
                    "ok": False,
                    "error": str(e),
                })
            return

        raise RuntimeError(f"unsupported stdio op: {op}")

    async def _call(self, origin: str, channel: str, payload: bytes, timeout_s: float) -> bytes:
        self._reply_counter += 1
        reply_channel = f"_REPLY.{self._reply_counter}"

        fut: asyncio.Future[bytes] = self.loop.create_future()
        self._pending_replies[reply_channel] = fut

        try:
            delivered = self._dispatch_event(
                channel=channel,
                payload=payload,
                reply_channel=reply_channel,
                limit_one=True,
            )
            if not delivered:
                await asyncio.sleep(timeout_s)
                raise asyncio.TimeoutError()

            return await asyncio.wait_for(fut, timeout_s)
        finally:
            self._pending_replies.pop(reply_channel, None)

    async def _send(self, origin: str, channel: str, payload: bytes, reply_channel: str | None):
        pending = self._pending_replies.get(channel)
        if pending and not pending.done():
            pending.set_result(payload)
            return

        self._dispatch_event(
            channel=channel,
            payload=payload,
            reply_channel=reply_channel,
            limit_one=False,
        )

    def _dispatch_event(self, channel: str, payload: bytes, reply_channel: str | None, limit_one: bool) -> bool:
        lids = list(self._channels_to_lids.get(channel, []))
        if not lids:
            return False

        delivered = 0
        for lid in lids:
            state = self._listeners.get(lid)
            if state is None:
                continue

            if state.endpoint == "runner":
                cb = state.callback
                if cb is not None:
                    msg = TransportMessage(
                        payload=payload,
                        reply_channel=reply_channel,
                        _client=self._runner_client,
                    )
                    task = self.loop.create_task(cb(msg))
                    task.add_done_callback(_log_task_exception)
                    delivered += 1
            else:
                endpoint = self._remote_endpoints.get(state.endpoint)
                if endpoint is None:
                    continue
                endpoint.send_json({
                    "op": "event",
                    "lid": state.lid,
                    "channel": channel,
                    "reply_channel": reply_channel,
                    "payload": _encode_bytes(payload),
                })
                delivered += 1

            if state.remaining_events is not None:
                state.remaining_events -= 1
                if state.remaining_events <= 0:
                    self._remove_listener(state.lid)

            if limit_one and delivered > 0:
                break

        return delivered > 0

    def _register_listener(self, state: _ListenerState):
        old = self._listeners.get(state.lid)
        if old is not None:
            self._remove_listener(old.lid)

        self._listeners[state.lid] = state
        self._channels_to_lids.setdefault(state.channel, []).append(state.lid)

    def _remove_listener(self, lid: str):
        state = self._listeners.pop(lid, None)
        if state is None:
            return

        lid_list = self._channels_to_lids.get(state.channel, [])
        lid_list = [e for e in lid_list if e != lid]
        if lid_list:
            self._channels_to_lids[state.channel] = lid_list
        else:
            self._channels_to_lids.pop(state.channel, None)

        if state.endpoint != "runner":
            self._endpoint_lids.setdefault(state.endpoint, set()).discard(lid)

    def _remove_endpoint(self, endpoint_name: str):
        lids = list(self._endpoint_lids.get(endpoint_name, set()))
        for lid in lids:
            self._remove_listener(lid)
        self._endpoint_lids.pop(endpoint_name, None)
        self._remote_endpoints.pop(endpoint_name, None)


def _log_task_exception(task: asyncio.Task):
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"[stdio-bus] callback task failed: {e}", flush=True)


def _log_threadsafe_future(fut, endpoint_name: str):
    try:
        fut.result()
    except Exception as e:
        print(f"[stdio-bus] failed handling frame from {endpoint_name}: {e}", flush=True)
