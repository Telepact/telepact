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

from typing import cast, TYPE_CHECKING

from ..Message import Message
from ..SerializerMeasurement import (
    SerializerMeasurementObserver,
    annotate_serializer_measurement,
    measure_serializer_stage,
    run_measured_serializer_operation,
)
from ..internal.validation.InvalidMessage import InvalidMessage
from ..internal.validation.InvalidMessageBody import InvalidMessageBody

if TYPE_CHECKING:
    from ..Serialization import Serialization
    from ..internal.binary.BinaryEncoder import BinaryEncoder
    from ..internal.binary.Base64Encoder import Base64Encoder


def deserialize_internal(message_bytes: bytes, serializer: 'Serialization',
                          binary_encoder: 'BinaryEncoder',
                          base64_encoder: 'Base64Encoder',
                          measurement_observer: SerializerMeasurementObserver | None = None) -> 'Message':
    def _run() -> 'Message':
        message_as_pseudo_json: object
        is_msg_pack: bool

        try:
            if message_bytes[0] == 0x92:  # MsgPack
                is_msg_pack = True
                annotate_serializer_measurement(
                    transport_encoding="msgpack",
                    protocol_encoding="binary",
                )
                message_as_pseudo_json = measure_serializer_stage(
                    "deserialize.msgpack.decode",
                    lambda: serializer.from_msgpack(message_bytes),
                )
            else:
                is_msg_pack = False
                annotate_serializer_measurement(
                    transport_encoding="json",
                    protocol_encoding="base64",
                )
                message_as_pseudo_json = measure_serializer_stage(
                    "deserialize.json.decode",
                    lambda: serializer.from_json(message_bytes),
                )
        except Exception as e:
            raise InvalidMessage() from e

        if not isinstance(message_as_pseudo_json, list):
            raise InvalidMessage()

        message_as_pseudo_json_list = cast(list[object], message_as_pseudo_json)

        if len(message_as_pseudo_json_list) != 2:
            raise InvalidMessage()

        final_message_as_pseudo_json_list: list[object]
        if is_msg_pack:
            final_message_as_pseudo_json_list = measure_serializer_stage(
                "deserialize.binary.decode",
                lambda: binary_encoder.decode(message_as_pseudo_json_list),
            )
            headers_obj = final_message_as_pseudo_json_list[0]
            annotate_serializer_measurement(
                packed=isinstance(headers_obj, dict) and headers_obj.get("@pac_") is True,
            )
        else:
            final_message_as_pseudo_json_list = measure_serializer_stage(
                "deserialize.base64.decode",
                lambda: base64_encoder.decode(message_as_pseudo_json_list),
            )
            headers_obj = final_message_as_pseudo_json_list[0]
            annotate_serializer_measurement(
                packed=isinstance(headers_obj, dict) and headers_obj.get("@pac_") is True,
            )

        def _validate() -> 'Message':
            if not isinstance(final_message_as_pseudo_json_list[0], dict):
                raise InvalidMessage()

            headers = cast(dict[str, object], final_message_as_pseudo_json_list[0])

            if not isinstance(final_message_as_pseudo_json_list[1], dict):
                raise InvalidMessage()

            body = cast(dict[str, object], final_message_as_pseudo_json_list[1])

            if len(body) != 1:
                raise InvalidMessageBody()

            if not isinstance(next(iter(body.values())), dict):
                raise InvalidMessageBody()

            return Message(headers, body)

        return cast(Message, measure_serializer_stage("deserialize.validation", _validate))

    return run_measured_serializer_operation(
        "deserialize",
        measurement_observer,
        binary_requested=False,
        transport_encoding="json",
        protocol_encoding="base64",
        packed=False,
        fell_back_to_json=False,
        fn=_run,
    )
