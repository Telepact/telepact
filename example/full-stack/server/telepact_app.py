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
import json
import logging
import threading
from collections import deque
from contextvars import ContextVar
from copy import deepcopy
from dataclasses import dataclass
from http.cookies import SimpleCookie
from pathlib import Path
from time import perf_counter

from telepact import FunctionRouter, Message, Server, TelepactError, TelepactSchema, TelepactSchemaFiles

EXAMPLE_DIR = Path(__file__).resolve().parent.parent
RECENT_EVENT_LIMIT = 20

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger('telepact.example.full_stack')


@dataclass(frozen=True)
class SessionIdentity:
    user_id: str
    role: str
    display_name: str


@dataclass(frozen=True)
class TelepactHttpResponse:
    response_bytes: bytes
    content_type: str


VALID_SESSIONS = {
    'demo-user-session': SessionIdentity('user-123', 'reader', 'Demo Reader'),
    'demo-admin-session': SessionIdentity('admin-007', 'admin', 'Demo Admin'),
}

_METRICS_LOCK = threading.Lock()
_METRICS: dict[str, object] = {
    'requestCount': 0,
    'unauthorizedCount': 0,
    'unknownErrorCount': 0,
    'lastRequestId': None,
    'byFunction': {},
}
_RECENT_EVENTS: deque[dict[str, object]] = deque(maxlen=RECENT_EVENT_LIMIT)
_REQUEST_CONTEXT: ContextVar[dict[str, object]] = ContextVar('request_context', default={})

files = TelepactSchemaFiles(str(EXAMPLE_DIR / 'api'))
schema = TelepactSchema.from_file_json_map(files.filenames_to_json)
options = Server.Options()


def _replace_context(context: dict[str, object]) -> None:
    _REQUEST_CONTEXT.set(context)


def _merge_context(**updates: object) -> dict[str, object]:
    current = dict(_REQUEST_CONTEXT.get())
    current.update({key: value for key, value in updates.items() if value is not None})
    _replace_context(current)
    return current


def _append_event(event_type: str, **fields: object) -> None:
    event = {'type': event_type, **fields}
    with _METRICS_LOCK:
        _RECENT_EVENTS.append(event)
    log.info(json.dumps(event, sort_keys=True))


def _record_metric(function_name: str, outcome: str, duration_ms: float, request_id: str | None) -> None:
    with _METRICS_LOCK:
        _METRICS['requestCount'] = int(_METRICS['requestCount']) + 1
        _METRICS['lastRequestId'] = request_id
        if outcome == 'ErrorUnauthorized_':
            _METRICS['unauthorizedCount'] = int(_METRICS['unauthorizedCount']) + 1
        if outcome == 'ErrorUnknown_':
            _METRICS['unknownErrorCount'] = int(_METRICS['unknownErrorCount']) + 1

        by_function = _METRICS['byFunction']
        assert isinstance(by_function, dict)
        function_metrics = by_function.setdefault(function_name, {
            'calls': 0,
            'totalDurationMs': 0.0,
            'outcomes': {},
        })
        assert isinstance(function_metrics, dict)
        function_metrics['calls'] = int(function_metrics['calls']) + 1
        function_metrics['totalDurationMs'] = float(function_metrics['totalDurationMs']) + duration_ms
        outcomes = function_metrics['outcomes']
        assert isinstance(outcomes, dict)
        outcomes[outcome] = int(outcomes.get(outcome, 0)) + 1


def snapshot_ops_state() -> dict[str, object]:
    with _METRICS_LOCK:
        metrics = deepcopy(_METRICS)
        events = list(_RECENT_EVENTS)

    by_function = metrics.get('byFunction', {})
    if isinstance(by_function, dict):
        for value in by_function.values():
            if isinstance(value, dict):
                calls = int(value.get('calls', 0))
                total_duration_ms = float(value.get('totalDurationMs', 0.0))
                value['averageDurationMs'] = round(total_duration_ms / calls, 2) if calls else 0.0
                value['totalDurationMs'] = round(total_duration_ms, 2)

    return {
        'metrics': metrics,
        'recentEvents': events,
    }


def read_session_cookie(cookie_header: str | None) -> str | None:
    if not cookie_header:
        return None

    cookie = SimpleCookie()
    cookie.load(cookie_header)
    session = cookie.get('session')
    return session.value if session is not None else None


def normalized_identity(session_token: str | None) -> SessionIdentity | None:
    if session_token is None:
        return None
    return VALID_SESSIONS.get(session_token)


async def on_auth(headers: dict[str, object]) -> dict[str, object]:
    auth = headers.get('.auth_')
    session = auth.get('Session') if isinstance(auth, dict) else None
    token = session.get('token') if isinstance(session, dict) else None
    identity = normalized_identity(token if isinstance(token, str) else None)
    if identity is None:
        return {}

    _merge_context(userId=identity.user_id, role=identity.role, displayName=identity.display_name)
    return {
        '.userId': identity.user_id,
        '.role': identity.role,
        '@displayName': identity.display_name,
    }


options.on_auth = on_auth


def on_request(message: Message) -> None:
    _merge_context(functionName=message.get_body_target(), startedAt=perf_counter())


options.on_request = on_request


def on_response(message: Message) -> None:
    context = dict(_REQUEST_CONTEXT.get())
    function_name = str(context.get('functionName', 'unknown'))
    request_id = context.get('requestId')
    user_id = context.get('userId', 'anonymous')
    role = context.get('role', 'anonymous')
    started_at = context.get('startedAt')
    duration_ms = round((perf_counter() - float(started_at)) * 1000, 2) if isinstance(started_at, (int, float)) else 0.0
    outcome = message.get_body_target()
    case_id = context.get('caseId')

    _record_metric(function_name, outcome, duration_ms, request_id if isinstance(request_id, str) else None)
    _append_event(
        'telepact.response',
        requestId=request_id,
        function=function_name,
        userId=user_id,
        role=role,
        outcome=outcome,
        durationMs=duration_ms,
        caseId=case_id,
    )


options.on_response = on_response


def on_error(error: TelepactError) -> None:
    context = _merge_context(caseId=error.case_id, errorKind=error.kind)
    _append_event(
        'telepact.error',
        requestId=context.get('requestId'),
        function=context.get('functionName', 'unknown'),
        caseId=error.case_id,
        kind=error.kind,
        message=str(error),
    )
    log.exception('telepact error case_id=%s', error.case_id, exc_info=error)


options.on_error = on_error


async def middleware(request_message: Message, function_router: FunctionRouter) -> Message:
    _merge_context(functionName=request_message.get_body_target())
    return await function_router.route(request_message)


options.middleware = middleware


async def me(_function_name: str, request_message: Message) -> Message:
    user_id = request_message.headers.get('.userId')
    role = request_message.headers.get('.role')
    display_name = request_message.headers.get('@displayName')
    if not isinstance(user_id, str) or not isinstance(role, str) or not isinstance(display_name, str):
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'missing or invalid session cookie',
            },
        })

    return Message({}, {
        'Ok_': {
            'userId': user_id,
            'role': role,
            'displayName': display_name,
        },
    })


async def admin_report(_function_name: str, request_message: Message) -> Message:
    if request_message.headers.get('.userId') is None:
        return Message({}, {
            'ErrorUnauthenticated_': {
                'message!': 'sign in before requesting the admin report',
            },
        })

    if request_message.headers.get('.role') != 'admin':
        return Message({}, {
            'ErrorUnauthorized_': {
                'message!': 'admin role required',
            },
        })

    metrics = snapshot_ops_state()['metrics']
    assert isinstance(metrics, dict)
    return Message({}, {
        'Ok_': {
            'requestCount': int(metrics['requestCount']),
            'unauthorizedCount': int(metrics['unauthorizedCount']),
            'unknownErrorCount': int(metrics['unknownErrorCount']),
            'lastRequestId': metrics['lastRequestId'],
        },
    })


async def trigger_failure(_function_name: str, request_message: Message) -> Message:
    actor = request_message.headers.get('@displayName', 'anonymous caller')
    raise RuntimeError(f'demo bug for {actor}')


function_router = FunctionRouter()
function_router.register_authenticated_routes({
    'fn.me': me,
    'fn.adminReport': admin_report,
    'fn.triggerFailure': trigger_failure,
})
telepact_server = Server(schema, function_router, options)


def process_telepact_request(request_bytes: bytes, request_id: str, session_token: str | None) -> TelepactHttpResponse:
    context_token = _REQUEST_CONTEXT.set({'requestId': request_id, 'transport': 'http'})
    loop = asyncio.new_event_loop()
    try:
        def update_headers(headers: dict[str, object]) -> None:
            headers['.requestId'] = request_id
            if session_token is not None:
                headers['.auth_'] = {'Session': {'token': session_token}}

        response = loop.run_until_complete(telepact_server.process(request_bytes, update_headers))
        content_type = 'application/octet-stream' if '.bin_' in response.headers else 'application/json'
        return TelepactHttpResponse(response_bytes=response.bytes, content_type=content_type)
    finally:
        loop.close()
        _REQUEST_CONTEXT.reset(context_token)
