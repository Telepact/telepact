#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

import asyncio
from typing import Callable, TYPE_CHECKING, cast, Awaitable

if TYPE_CHECKING:
    from ..Message import Message
    from ..Serializer import Serializer


async def client_handle_message(request_message: 'Message',
                                 adapter: Callable[['Message', 'Serializer'], Awaitable['Message']],
                                 serializer: 'Serializer',
                                 timeout_ms_default: int,
                                 use_binary_default: bool,
                                 always_send_json: bool) -> 'Message':
    from ..SerializationError import SerializationError
    from ..TelepactError import TelepactError

    header: dict[str, object] = request_message.headers

    try:
        if "@time_" not in header:
            header["@time_"] = timeout_ms_default

        if use_binary_default:
            header["@binary_"] = True

        if header.get('@binary_', False) and always_send_json:
            header["_forceSendJson"] = True

        timeout_ms = cast(int, header.get("@time_"))

        async with asyncio.timeout(timeout_ms / 1000):
            response_message = await adapter(request_message, serializer)

        if response_message.body == {"ErrorParseFailure_": {"reasons": [{"IncompatibleBinaryEncoding": {}}]}}:
            header["@binary_"] = True
            header["_forceSendJson"] = True

            async with asyncio.timeout(timeout_ms / 1000):
                return await adapter(request_message, serializer)

        return response_message
    except Exception as e:
        if isinstance(e, TelepactError):
            raise
        if isinstance(e, SerializationError):
            raise TelepactError(
                "telepact client serialization or deserialization failed",
                kind="serialization",
                cause=e,
            ) from e
        if isinstance(e, TimeoutError):
            raise TelepactError(
                f"telepact client transport timed out after {timeout_ms}ms",
                kind="transport",
                cause=e,
            ) from e
        raise TelepactError(
            "telepact client transport failed",
            kind="transport",
            cause=e,
        ) from e
