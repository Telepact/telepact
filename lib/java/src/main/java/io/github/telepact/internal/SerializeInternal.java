//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal;

import java.util.List;
import java.util.Objects;
import java.util.function.Consumer;

import io.github.telepact.Message;
import io.github.telepact.Serialization;
import io.github.telepact.SerializationError;
import io.github.telepact.SerializerMeasurement;
import io.github.telepact.internal.binary.Base64Encoder;
import io.github.telepact.internal.binary.BinaryEncoder;
import io.github.telepact.internal.binary.BinaryEncoderUnavailableError;

public class SerializeInternal {
    public static byte[] serializeInternal(Message message, BinaryEncoder binaryEncoder,
            Base64Encoder base64Encoder,
            Serialization serializer,
            Consumer<SerializerMeasurement> measurementObserver) {
        final var headers = message.headers;
        final var binaryRequested = Objects.equals(true, headers.get("@binary_"));
        final var packed = Objects.equals(true, headers.get("@pac_"));

        return SerializerMeasurementSupport.runMeasuredSerializerOperation(
                "serialize",
                measurementObserver,
                binaryRequested,
                "json",
                "base64",
                packed,
                false,
                () -> {
                    final boolean[] serializeAsBinary = { false };
                    SerializerMeasurementSupport.measureSerializerStage("serialize.headerDecision", () -> {
                        if (headers.containsKey("@binary_")) {
                            serializeAsBinary[0] = Objects.equals(true, headers.remove("@binary_"));
                        } else {
                            serializeAsBinary[0] = false;
                        }
                    });

                    final List<Object> messageAsPseudoJson = List.of(message.headers, message.body);

                    try {
                        if (serializeAsBinary[0]) {
                            try {
                                final var encodedMessage = SerializerMeasurementSupport.measureSerializerStage(
                                        "serialize.binary.encode",
                                        () -> binaryEncoder.encode(messageAsPseudoJson));
                                SerializerMeasurementSupport.annotateSerializerMeasurement(
                                        null,
                                        "msgpack",
                                        "binary",
                                        null,
                                        false);
                                return SerializerMeasurementSupport.measureSerializerStageThrowable(
                                        "serialize.msgpack.encode",
                                        () -> serializer.toMsgPack(encodedMessage));
                            } catch (BinaryEncoderUnavailableError e) {
                                SerializerMeasurementSupport.annotateSerializerMeasurement(
                                        null,
                                        "json",
                                        "base64",
                                        null,
                                        true);
                                final var base64EncodedMessage = SerializerMeasurementSupport.measureSerializerStage(
                                        "serialize.base64.encode",
                                        () -> base64Encoder.encode(messageAsPseudoJson));
                                return SerializerMeasurementSupport.measureSerializerStageThrowable(
                                        "serialize.json.encode",
                                        () -> serializer.toJson(base64EncodedMessage));
                            }
                        }

                        final var base64EncodedMessage = SerializerMeasurementSupport.measureSerializerStage(
                                "serialize.base64.encode",
                                () -> base64Encoder.encode(messageAsPseudoJson));
                        SerializerMeasurementSupport.annotateSerializerMeasurement(
                                null,
                                "json",
                                "base64",
                                null,
                                false);
                        return SerializerMeasurementSupport.measureSerializerStageThrowable(
                                "serialize.json.encode",
                                () -> serializer.toJson(base64EncodedMessage));
                    } catch (Throwable e) {
                        throw new SerializationError(
                                e,
                                serializeAsBinary[0] ? "encoding Telepact message as binary or JSON fallback"
                                        : "encoding Telepact message as JSON");
                    }
                });
    }
}
