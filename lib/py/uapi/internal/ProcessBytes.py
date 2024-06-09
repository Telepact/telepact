from typing import List, Dict, Any, Callable, TYPE_CHECKING

from uapi.Message import Message

if TYPE_CHECKING:
    from uapi.Serializer import Serializer
    from uapi.UApiSchema import UApiSchema


def process_bytes(request_message_bytes: bytes, serializer: 'Serializer', uapi_schema: 'UApiSchema',
                  on_error: Callable[[Exception], None], on_request: Callable[['Message'], None],
                  on_response: Callable[['Message'], None], handler: Callable[['Message'], 'Message']) -> bytes:
    from uapi.internal.HandleMessage import handle_message
    from uapi.internal.ParseRequestMessage import parse_request_message

    try:
        request_message = parse_request_message(
            request_message_bytes, serializer, uapi_schema, on_error)

        try:
            on_request(request_message)
        except Exception:
            pass

        response_message = handle_message(
            request_message, uapi_schema, handler, on_error)

        try:
            on_response(response_message)
        except Exception:
            pass

        return serializer.serialize(response_message)
    except Exception as e:
        try:
            on_error(e)
        except Exception:
            pass

        return serializer.serialize(Message({}, {"ErrorUnknown_": {}}))
