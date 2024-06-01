from typing import Any, Callable, Dict, List, Union
from concurrent.futures import Future
from uapi import Message, Serializer, UApiError


def process_request_object(request_message: Message,
                           adapter: Callable[[Message, Serializer], Future[Message]],
                           serializer: Serializer,
                           timeout_ms_default: int,
                           use_binary_default: bool) -> Message:
    header: Dict[str, Any] = request_message.header

    try:
        if "tim_" not in header:
            header["tim_"] = timeout_ms_default

        if use_binary_default:
            header["_binary"] = True

        timeout_ms = int(header["tim_"])

        response_message = adapter(
            request_message, serializer).result(timeout_ms / 1000)

        if response_message.body == {"ErrorParseFailure_": {"reasons": [{"IncompatibleBinaryEncoding": {}}]}}:
            # Try again, but as json
            header["_binary"] = True
            header["_forceSendJson"] = True

            return adapter(request_message, serializer).result(timeout_ms / 1000)

        return response_message
    except Exception as e:
        raise UApiError(e)
