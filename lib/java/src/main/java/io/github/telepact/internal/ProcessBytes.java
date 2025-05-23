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

import static io.github.telepact.internal.HandleMessage.handleMessage;
import static io.github.telepact.internal.ParseRequestMessage.parseRequestMessage;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;

import io.github.telepact.Message;
import io.github.telepact.TelepactSchema;
import io.github.telepact.Serializer;

public class ProcessBytes {
    public static byte[] processBytes(byte[] requestMessageBytes, Serializer serializer, TelepactSchema telepactSchema,
            Consumer<Throwable> onError, Consumer<Message> onRequest, Consumer<Message> onResponse,
            Function<Message, Message> handler) {
        try {
            final var requestMessage = parseRequestMessage(requestMessageBytes, serializer,
                    telepactSchema, onError);

            try {
                onRequest.accept(requestMessage);
            } catch (Throwable ignored) {
            }

            final var responseMessage = handleMessage(requestMessage, telepactSchema, handler, onError);

            try {
                onResponse.accept(responseMessage);
            } catch (Throwable ignored) {
            }

            return serializer.serialize(responseMessage);
        } catch (Throwable e) {
            try {
                onError.accept(e);
            } catch (Throwable ignored) {
            }

            return serializer
                    .serialize(new Message(new HashMap<>(), Map.of("ErrorUnknown_", Map.of())));
        }
    }
}
