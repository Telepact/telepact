# 23. Logging

For server-side observability, the two main hooks are middleware and `on_error`.

## Install the Python library

```sh
pip install --pre telepact
```

## Add logging to the minimum server

Here is the interesting part of `server.py`:

```py
import asyncio
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telepact import Message, Server, TelepactError, TelepactSchema


logging.basicConfig(level=logging.INFO)
log = logging.getLogger('hello-server')

schema = TelepactSchema.from_directory('./api')

options = Server.Options()
options.auth_required = False


async def middleware(request_message: Message, function_router) -> Message:
    function_name = request_message.get_body_target()
    log.info('start %s', function_name)
    try:
        return await function_router.route(request_message)
    finally:
        log.info('finish %s', function_name)


options.middleware = middleware


def on_error(error: Exception) -> None:
    if isinstance(error, TelepactError):
        log.exception('telepact error case_id=%s', error.case_id, exc_info=error)
    else:
        log.exception('telepact error', exc_info=error)


options.on_error = on_error


async def hello(function_name: str, request_message: Message) -> Message:
    if request_message.body[function_name]['name'] == 'boom':
        raise RuntimeError('unexpected bug')
    return Message({}, {'Ok_': {'message': 'hello'}})
```

## Run the server on port 8002

```sh
python server.py
```

## See normal logging

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.hello": {"name": "Telepact"}}]'
```

We should see middleware logs around the request.

## See error logging

```sh
curl -s localhost:8002/api/telepact -d '[{}, {"fn.hello": {"name": "boom"}}]'
```

Response:

```json
[{}, {"ErrorUnknown_": {"caseId": "5941539f-127c-4c4d-8194-1648f679be92"}}]
```

And the server logs should contain the actual stack trace with the same
`case_id=5941539f-127c-4c4d-8194-1648f679be92`. That is the main operational
pattern: keep the wire response generic, and use the case ID to match a
client-side `ErrorUnknown_` report to the corresponding server-side log entry.

Next: [24. Server auth](./24-server-auth.md)
