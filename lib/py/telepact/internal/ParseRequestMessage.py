#|
#|  Copyright The Telepact Authors
#|
#|  Licensed under the Apache License, Version 2.0 (the "License");
#|  you may not use this file except in compliance with the License.
#|  You may obtain a copy of the License at
#|
#|  https://www.apache.org/licenses/LICENSE-2.0
#|
#|  Unless required by applicable law or agreed to in writing, software
#|  distributed under the License is distributed on an "AS IS" BASIS,
#|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#|  See the License for the specific language governing permissions and
#|  limitations under the License.
#|

from typing import Callable, TYPE_CHECKING, NamedTuple

from ..Message import Message
from ..internal.DeserializeInternal import RequestDeserializeError
from ..internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from ..internal.binary.BinaryEncodingMissing import BinaryEncodingMissing
from ..internal.validation.InvalidMessage import InvalidMessage
from ..internal.validation.InvalidMessageBody import InvalidMessageBody
from ..TelepactError import TelepactError

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..TelepactSchema import TelepactSchema


class RequestParseSuccess(NamedTuple):
    message: Message


class RequestParseFailure(NamedTuple):
    parse_failures: list[dict[str, object]]
    response_headers: dict[str, object]


RequestParseResult = RequestParseSuccess | RequestParseFailure


def parse_request_message(request_message_bytes: bytes, serializer: 'Serializer', telepact_schema: 'TelepactSchema',
                           on_error: Callable[[TelepactError], None]) -> 'RequestParseResult':
    try:
        return RequestParseSuccess(serializer.deserialize(request_message_bytes))
    except Exception as e:
        parse_exception = e.cause if isinstance(e, RequestDeserializeError) else e
        response_headers = e.response_headers if isinstance(e, RequestDeserializeError) else {}

        on_error(
            TelepactError(
                "telepact request parsing failed while decoding the incoming message",
                kind="parse",
                cause=parse_exception,
            )
        )

        if isinstance(parse_exception, BinaryEncoderUnavailableError):
            reason = "IncompatibleBinaryEncoding"
        elif isinstance(parse_exception, BinaryEncodingMissing):
            reason = "BinaryDecodeFailure"
        elif isinstance(parse_exception, InvalidMessage):
            reason = "ExpectedJsonArrayOfTwoObjects"
        elif isinstance(parse_exception, InvalidMessageBody):
            reason = "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject"
        else:
            reason = "ExpectedJsonArrayOfTwoObjects"

        return RequestParseFailure(parse_failures=[{reason: {}}], response_headers=response_headers)
