from typing import Callable, TYPE_CHECKING

from ..Message import Message
from ..internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from ..internal.binary.BinaryEncodingMissing import BinaryEncodingMissing
from ..internal.validation.InvalidMessage import InvalidMessage
from ..internal.validation.InvalidMessageBody import InvalidMessageBody

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..UApiSchema import UApiSchema


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
