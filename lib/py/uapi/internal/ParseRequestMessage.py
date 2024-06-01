from typing import List, Dict, Callable

from uapi.Message import Message
from uapi.Serializer import Serializer
from uapi.UApiSchema import UApiSchema
from uapi.internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from uapi.internal.binary.BinaryEncodingMissing import BinaryEncodingMissing
from uapi.internal.validation.InvalidMessage import InvalidMessage
from uapi.internal.validation.InvalidMessageBody import InvalidMessageBody


def parse_request_message(request_message_bytes: bytes, serializer: 'Serializer', uapi_schema: 'UApiSchema',
                          on_error: Callable[[Exception], None]) -> 'Message':
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
