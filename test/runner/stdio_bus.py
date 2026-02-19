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
class Msg:
    data: bytes
    reply: str | None


@dataclass
class RequestResponse:
    data: bytes


@dataclass
class _SubscriptionState:
    sid: str
    endpoint: str
    subject: str
    callback: Callable[[Msg], Awaitable[None]] | None = None
    remaining_messages: int | None = None


class RunnerSubscription:
    def __init__(self, bus: "StdioBus", sid: str):
        self._bus = bus
        self._sid = sid

    async def unsubscribe(self, limit: int | None = None):
        await self._bus.unsubscribe_runner(self._sid, limit=limit)

    async def drain(self):
        await self.unsubscribe()


class RunnerClient:
    def __init__(self, bus: "StdioBus"):
        self._bus = bus

    async def request(self, subject: str, data: bytes, timeout: float = 1):
        response = await self._bus.request_from_runner(subject, data, timeout)
        return RequestResponse(data=response)

    async def publish(self, subject: str, data: bytes):
        await self._bus.publish_from_runner(subject, data)

    async def subscribe(self, subject: str, cb: Callable[[Msg], Awaitable[None]]):
        return await self._bus.subscribe_runner(subject, cb)


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
        self._sid_counter = 0
        self._inbox_counter = 0

        self._subscriptions: dict[str, _SubscriptionState] = {}
        self._subjects_to_sids: dict[str, list[str]] = {}

        self._pending_replies: dict[str, asyncio.Future[bytes]] = {}
        self._remote_endpoints: dict[str, _RemoteEndpoint] = {}
        self._endpoint_sids: dict[str, set[str]] = {}

    def client(self) -> RunnerClient:
        return RunnerClient(self)

    async def close(self):
        # No-op: fixture teardown owns child process lifecycle.
        return

    async def subscribe_runner(self, subject: str, cb: Callable[[Msg], Awaitable[None]]):
        self._sid_counter += 1
        sid = f"runner-{self._sid_counter}"
        state = _SubscriptionState(
            sid=sid,
            endpoint="runner",
            subject=subject,
            callback=cb,
        )
        self._register_subscription(state)
        return RunnerSubscription(self, sid)

    async def unsubscribe_runner(self, sid: str, limit: int | None = None):
        state = self._subscriptions.get(sid)
        if not state or state.endpoint != "runner":
            return

        if limit is None:
            self._remove_subscription(sid)
            return

        if limit <= 0:
            self._remove_subscription(sid)
            return

        state.remaining_messages = limit

    async def request_from_runner(self, subject: str, data: bytes, timeout_s: float):
        return await self._request("runner", subject, data, timeout_s)

    async def publish_from_runner(self, subject: str, data: bytes):
        await self._publish("runner", subject, data, reply=None)

    def attach_process(self, endpoint_name: str, process: subprocess.Popen):
        endpoint = _RemoteEndpoint(endpoint_name, process)
        self._remote_endpoints[endpoint_name] = endpoint
        self._endpoint_sids.setdefault(endpoint_name, set())

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
        if op == "subscribe":
            sid = frame["sid"]
            subject = frame["subject"]
            state = _SubscriptionState(
                sid=sid,
                endpoint=endpoint_name,
                subject=subject,
                callback=None,
            )
            self._register_subscription(state)
            self._endpoint_sids.setdefault(endpoint_name, set()).add(sid)
            return

        if op == "unsubscribe":
            sid = frame["sid"]
            self._remove_subscription(sid)
            self._endpoint_sids.setdefault(endpoint_name, set()).discard(sid)
            return

        if op == "publish":
            subject = frame["subject"]
            data = _decode_bytes(frame["data"])
            reply = frame.get("reply")
            await self._publish(endpoint_name, subject, data, reply=reply)
            return

        if op == "request":
            rid = frame["rid"]
            subject = frame["subject"]
            data = _decode_bytes(frame["data"])
            timeout_ms = int(frame.get("timeout_ms", 5000))
            endpoint = self._remote_endpoints.get(endpoint_name)
            if endpoint is None:
                return

            try:
                response_bytes = await self._request(
                    endpoint_name,
                    subject,
                    data,
                    timeout_s=max(timeout_ms, 1) / 1000.0,
                )
                endpoint.send_json({
                    "op": "request_result",
                    "rid": rid,
                    "ok": True,
                    "data": _encode_bytes(response_bytes),
                })
            except asyncio.TimeoutError:
                endpoint.send_json({
                    "op": "request_result",
                    "rid": rid,
                    "ok": False,
                    "error": "timeout",
                })
            except Exception as e:
                endpoint.send_json({
                    "op": "request_result",
                    "rid": rid,
                    "ok": False,
                    "error": str(e),
                })
            return

        raise RuntimeError(f"unsupported stdio op: {op}")

    async def _request(self, origin: str, subject: str, data: bytes, timeout_s: float) -> bytes:
        self._inbox_counter += 1
        reply_subject = f"_INBOX.{self._inbox_counter}"

        fut: asyncio.Future[bytes] = self.loop.create_future()
        self._pending_replies[reply_subject] = fut

        try:
            delivered = self._deliver(
                subject=subject,
                data=data,
                reply=reply_subject,
                limit_one=True,
            )
            if not delivered:
                # Keep timeout semantics consistent with request/reply transports.
                await asyncio.sleep(timeout_s)
                raise asyncio.TimeoutError()

            return await asyncio.wait_for(fut, timeout_s)
        finally:
            self._pending_replies.pop(reply_subject, None)

    async def _publish(self, origin: str, subject: str, data: bytes, reply: str | None):
        pending = self._pending_replies.get(subject)
        if pending and not pending.done():
            pending.set_result(data)
            return

        self._deliver(
            subject=subject,
            data=data,
            reply=reply,
            limit_one=False,
        )

    def _deliver(self, subject: str, data: bytes, reply: str | None, limit_one: bool) -> bool:
        sids = list(self._subjects_to_sids.get(subject, []))
        if not sids:
            return False

        delivered = 0
        for sid in sids:
            state = self._subscriptions.get(sid)
            if state is None:
                continue

            if state.endpoint == "runner":
                cb = state.callback
                if cb is not None:
                    msg = Msg(data=data, reply=reply)
                    task = self.loop.create_task(cb(msg))
                    task.add_done_callback(_log_task_exception)
                    delivered += 1
            else:
                endpoint = self._remote_endpoints.get(state.endpoint)
                if endpoint is None:
                    continue
                endpoint.send_json({
                    "op": "message",
                    "sid": state.sid,
                    "subject": subject,
                    "reply": reply,
                    "data": _encode_bytes(data),
                })
                delivered += 1

            if state.remaining_messages is not None:
                state.remaining_messages -= 1
                if state.remaining_messages <= 0:
                    self._remove_subscription(state.sid)

            if limit_one and delivered > 0:
                break

        return delivered > 0

    def _register_subscription(self, state: _SubscriptionState):
        old = self._subscriptions.get(state.sid)
        if old is not None:
            self._remove_subscription(old.sid)

        self._subscriptions[state.sid] = state
        self._subjects_to_sids.setdefault(state.subject, []).append(state.sid)

    def _remove_subscription(self, sid: str):
        state = self._subscriptions.pop(sid, None)
        if state is None:
            return

        sid_list = self._subjects_to_sids.get(state.subject, [])
        sid_list = [e for e in sid_list if e != sid]
        if sid_list:
            self._subjects_to_sids[state.subject] = sid_list
        else:
            self._subjects_to_sids.pop(state.subject, None)

        if state.endpoint != "runner":
            self._endpoint_sids.setdefault(state.endpoint, set()).discard(sid)

    def _remove_endpoint(self, endpoint_name: str):
        sids = list(self._endpoint_sids.get(endpoint_name, set()))
        for sid in sids:
            self._remove_subscription(sid)
        self._endpoint_sids.pop(endpoint_name, None)
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
