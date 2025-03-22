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

import io.github.telepact.Message;
import io.github.telepact.Serialization;
import io.github.telepact.SerializationError;
import io.github.telepact.internal.binary.BinaryEncoder;
import io.github.telepact.internal.binary.BinaryEncoderUnavailableError;

public class SerializeInternal {
    public static byte[] serializeInternal(Message message, BinaryEncoder binaryEncoder,
            Serialization serializer) {
        final var headers = message.headers;

        final boolean serializeAsBinary;
        if (headers.containsKey("@binary_")) {
            serializeAsBinary = Objects.equals(true, headers.remove("@binary_"));
        } else {
            serializeAsBinary = false;
        }

        final List<Object> messageAsPseudoJson = List.of(message.headers, message.body);

        try {
            if (serializeAsBinary) {
                try {
                    final var encodedMessage = binaryEncoder.encode(messageAsPseudoJson);
                    return serializer.toMsgPack(encodedMessage);
                } catch (BinaryEncoderUnavailableError e) {
                    // We can still submit as json
                    return serializer.toJson(messageAsPseudoJson);
                }
            } else {
                return serializer.toJson(messageAsPseudoJson);
            }
        } catch (Throwable e) {
            throw new SerializationError(e);
        }
    }
}
