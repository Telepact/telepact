#|
#|  Copyright The Telepact Authors
#|  SPDX-License-Identifier: Apache-2.0
#|

from typing import Callable, TYPE_CHECKING

from ..Message import Message
from ..internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from ..internal.binary.BinaryEncodingMissing import BinaryEncodingMissing
from ..internal.validation.InvalidMessage import InvalidMessage
from ..internal.validation.InvalidMessageBody import InvalidMessageBody
from ..TelepactError import TelepactError

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..TelepactSchema import TelepactSchema


def parse_request_message(request_message_bytes: bytes, serializer: 'Serializer', telepact_schema: 'TelepactSchema',
                           on_error: Callable[[TelepactError], None]) -> 'Message':
    try:
        return serializer.deserialize(request_message_bytes)
    except Exception as e:
        on_error(
            TelepactError(
                "telepact request parsing failed while decoding the incoming message",
                kind="parse",
                cause=e,
            )
        )

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
