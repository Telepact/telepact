from typing import Callable, TYPE_CHECKING, Awaitable

from ..Message import Message

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..TelepactSchema import TelepactSchema


async def process_bytes(request_message_bytes: bytes, serializer: 'Serializer', telepact_schema: 'TelepactSchema',
                        on_error: Callable[[Exception], None], on_request: Callable[['Message'], None],
                        on_response: Callable[['Message'], None], handler: Callable[['Message'], Awaitable['Message']]) -> bytes:
    from ..internal.HandleMessage import handle_message
    from ..internal.ParseRequestMessage import parse_request_message

    try:
        request_message = parse_request_message(
            request_message_bytes, serializer, telepact_schema, on_error)

        try:
            on_request(request_message)
        except Exception:
            pass

        response_message = await handle_message(
            request_message, telepact_schema, handler, on_error)

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
