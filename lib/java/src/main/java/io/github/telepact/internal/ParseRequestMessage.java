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
import java.util.Map;
import java.util.function.Consumer;

import io.github.telepact.Message;
import io.github.telepact.TelepactSchema;
import io.github.telepact.Serializer;
import io.github.telepact.internal.binary.BinaryEncoderUnavailableError;
import io.github.telepact.internal.binary.BinaryEncodingMissing;
import io.github.telepact.internal.validation.InvalidMessage;
import io.github.telepact.internal.validation.InvalidMessageBody;

public class ParseRequestMessage {
    static Message parseRequestMessage(byte[] requestMessageBytes, Serializer serializer, TelepactSchema telepactSchema,
            Consumer<Throwable> onError) {

        try {
            return serializer.deserialize(requestMessageBytes);
        } catch (Exception e) {
            onError.accept(e);

            String reason;
            if (e instanceof BinaryEncoderUnavailableError) {
                reason = "IncompatibleBinaryEncoding";
            } else if (e instanceof BinaryEncodingMissing) {
                reason = "BinaryDecodeFailure";
            } else if (e instanceof InvalidMessage) {
                reason = "ExpectedJsonArrayOfTwoObjects";
            } else if (e instanceof InvalidMessageBody) {
                reason = "ExpectedJsonArrayOfAnObjectAndAnObjectOfOneObject";
            } else {
                reason = "ExpectedJsonArrayOfTwoObjects";
            }

            return new Message(Map.of("_parseFailures", List.of(Map.of(reason, Map.of()))),
                    Map.of("_unknown", Map.of()));
        }
    }
}
