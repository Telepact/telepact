import asyncio
from typing import Callable, TYPE_CHECKING, cast, Awaitable

if TYPE_CHECKING:
    from uapi.Message import Message
    from uapi.Serializer import Serializer


async def process_request_object(request_message: 'Message',
                                 adapter: Callable[['Message', 'Serializer'], Awaitable['Message']],
                                 serializer: 'Serializer',
                                 timeout_ms_default: int,
                                 use_binary_default: bool) -> 'Message':
    from uapi.UApiError import UApiError

    header: dict[str, object] = request_message.headers

    try:
        if "time_" not in header:
            header["time_"] = timeout_ms_default

        if use_binary_default:
            header["_binary"] = True

        timeout_ms = cast(int, header.get("time_"))

        async with asyncio.timeout(timeout_ms / 1000):
            response_message = await adapter(request_message, serializer)

        if response_message.body == {"ErrorParseFailure_": {"reasons": [{"IncompatibleBinaryEncoding": {}}]}}:
            header["_binary"] = True
            header["_forceSendJson"] = True

            async with asyncio.timeout(timeout_ms / 1000):
                return await adapter(request_message, serializer)

        return response_message
    except Exception as e:
        raise UApiError() from e
