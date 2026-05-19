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

from typing import TYPE_CHECKING

from ..internal.binary.BinaryEncoderUnavailableError import BinaryEncoderUnavailableError
from ..SerializerMeasurement import (
    SerializerMeasurementObserver,
    annotate_serializer_measurement,
    measure_serializer_stage,
    run_measured_serializer_operation,
)
from ..SerializationError import SerializationError

if TYPE_CHECKING:
    from ..Serialization import Serialization
    from ..Message import Message
    from ..internal.binary.BinaryEncoder import BinaryEncoder
    from ..internal.binary.Base64Encoder import Base64Encoder

def serialize_internal(message: 'Message', binary_encoder: 'BinaryEncoder',
                       base64_encoder: 'Base64Encoder',
                       serializer: 'Serialization',
                       measurement_observer: SerializerMeasurementObserver | None = None) -> bytes:
    headers: dict[str, object] = message.headers
    binary_requested = headers.get("@binary_") is True
    packed = headers.get("@pac_") is True

    def _run() -> bytes:
        serialize_as_binary: bool = False

        def _decide_headers() -> None:
            nonlocal serialize_as_binary
            if "@binary_" in headers:
                serialize_as_binary = headers.pop("@binary_") is True
            else:
                serialize_as_binary = False

        measure_serializer_stage("serialize.headerDecision", _decide_headers)
        message_as_pseudo_json: list[object] = [message.headers, message.body]

        try:
            if serialize_as_binary:
                try:
                    encoded_message = measure_serializer_stage(
                        "serialize.binary.encode",
                        lambda: binary_encoder.encode(message_as_pseudo_json),
                    )
                    annotate_serializer_measurement(
                        transport_encoding="msgpack",
                        protocol_encoding="binary",
                        fell_back_to_json=False,
                    )
                    return measure_serializer_stage("serialize.msgpack.encode", lambda: serializer.to_msgpack(encoded_message))
                except BinaryEncoderUnavailableError:
                    annotate_serializer_measurement(
                        transport_encoding="json",
                        protocol_encoding="base64",
                        fell_back_to_json=True,
                    )
                    base_64_encoded_message = measure_serializer_stage(
                        "serialize.base64.encode",
                        lambda: base64_encoder.encode(message_as_pseudo_json),
                    )
                    return measure_serializer_stage("serialize.json.encode", lambda: serializer.to_json(base_64_encoded_message))

            base_64_encoded_message = measure_serializer_stage(
                "serialize.base64.encode",
                lambda: base64_encoder.encode(message_as_pseudo_json),
            )
            annotate_serializer_measurement(
                transport_encoding="json",
                protocol_encoding="base64",
                fell_back_to_json=False,
            )
            return measure_serializer_stage("serialize.json.encode", lambda: serializer.to_json(base_64_encoded_message))
        except Exception as e:
            context = (
                "encoding Telepact message as binary or JSON fallback"
                if serialize_as_binary
                else "encoding Telepact message as JSON"
            )
            raise SerializationError(context=context, cause=e) from e

    return run_measured_serializer_operation(
        "serialize",
        measurement_observer,
        binary_requested=binary_requested,
        transport_encoding="json",
        protocol_encoding="base64",
        packed=packed,
        fell_back_to_json=False,
        fn=_run,
    )
