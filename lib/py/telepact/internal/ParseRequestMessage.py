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

from typing import Callable, TYPE_CHECKING

from ..Message import Message
from ..internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from ..internal.binary.BinaryEncodingMissing import BinaryEncodingMissing
from ..internal.validation.InvalidMessage import InvalidMessage
from ..internal.validation.InvalidMessageBody import InvalidMessageBody

if TYPE_CHECKING:
    from ..Serializer import Serializer
    from ..TelepactSchema import TelepactSchema


def parse_request_message(request_message_bytes: bytes, serializer: 'Serializer', telepact_schema: 'TelepactSchema',
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
