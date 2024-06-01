from typing import List, Dict, Callable
from uapi import Message, Serializer, UApiSchema
from uapi.internal.binary import BinaryEncoderUnavailableError, BinaryEncodingMissing
from uapi.internal.validation import InvalidMessage, InvalidMessageBody


def parse_request_message(request_message_bytes: bytes, serializer: Serializer, uapi_schema: UApiSchema,
                          on_error: Callable[[Exception], None]) -> Message:
    try:
        return serializer.deserialize(request_message_bytes)
    except Exception as e:
        on_error(e)

        if isinstance(e, BinaryEncoderUnavailableError):
            reason = "IncompatibleBinaryEncoding"
        elif isinstance(e, BinaryEncodingMissing):
            reason = "BinaryDecodeFailure"
        elif isinstance(e, InvalidMessage):
            reason = "ExpectedJsonArrayOfTwoObjects"
        elif isinstance(e, InvalidMessageBody):
            reason = "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject"
        else:
            reason = "ExpectedJsonArrayOfTwoObjects"

        return Message({"_parseFailures": [{reason: {}}]}, {"_unknown": {}})
