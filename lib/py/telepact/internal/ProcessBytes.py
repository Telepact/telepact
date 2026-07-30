#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import Callable, TYPE_CHECKING, Awaitable

from ..Message import Message
from ..SerializationError import SerializationError
from ..TelepactError import TelepactError
from ..internal.UnknownError import build_unknown_error_message

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..Server import AuthHandler, Middleware, FunctionRouter, UpdateHeaders
    from ..TelepactSchema import TelepactSchema
    from ..Response import Response


async def process_bytes(request_message_bytes: bytes, update_headers: 'UpdateHeaders | None',
                         serializer: 'Serializer', telepact_schema: 'TelepactSchema',
                         on_error: Callable[[TelepactError], None], on_request: Callable[['Message'], None],
                         on_response: Callable[['Message'], None], on_auth: 'AuthHandler',
                         middleware: 'Middleware', function_router: 'FunctionRouter') -> 'Response':
    from ..internal.HandleMessage import handle_message
    from ..internal.ParseRequestMessage import parse_request_message
    from ..Response import Response

    try:
        request_message = parse_request_message(
            request_message_bytes, serializer, telepact_schema, on_error)

        try:
            on_request(request_message)
        except Exception:
            pass

        response_message = await handle_message(
            request_message, update_headers, telepact_schema, middleware, function_router, on_error, on_auth)

        try:
            on_response(response_message)
        except Exception:
            pass

        try:
            response_bytes = serializer.serialize(response_message)
        except Exception as e:
            wrapped = (
                TelepactError(
                    "telepact response serialization failed",
                    kind="serialization",
                    cause=e,
                )
                if isinstance(e, SerializationError)
                else TelepactError(
                    "telepact server processing failed while serializing the response",
                    kind="serialization",
                    cause=e,
                )
            )
            try:
                on_error(wrapped)
            except Exception:
                pass
            response_bytes = serializer.serialize(build_unknown_error_message(wrapped))
            return Response(response_bytes, {})

        return Response(response_bytes, response_message.headers)
    except Exception as e:
        wrapped = e if isinstance(e, TelepactError) else TelepactError(
            "telepact server processing failed",
            cause=e,
        )
        try:
            on_error(wrapped)
        except Exception:
            pass

        response_bytes = serializer.serialize(build_unknown_error_message(wrapped))

        return Response(response_bytes, {})
