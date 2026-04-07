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
import io.github.telepact.Response;
import io.github.telepact.SerializationError;
import io.github.telepact.TelepactError;
import io.github.telepact.TelepactSchema;
import io.github.telepact.Serializer;
import io.github.telepact.Server.FunctionRouter;
import io.github.telepact.Server.Middleware;

public class ProcessBytes {
    public static Response processBytes(byte[] requestMessageBytes, Map<String, Object> overrideHeaders, Serializer serializer, TelepactSchema telepactSchema,
            Consumer<Throwable> onError, Consumer<Message> onRequest, Consumer<Message> onResponse,
            Function<Map<String, Object>, Map<String, Object>> onAuth,
            Middleware middleware, FunctionRouter functionRouter) {
        try {
            final var requestMessage = parseRequestMessage(requestMessageBytes, serializer,
                    telepactSchema, onError);

            try {
                onRequest.accept(requestMessage);
            } catch (Throwable ignored) {
            }

            final var responseMessage = handleMessage(requestMessage, overrideHeaders, telepactSchema, middleware, functionRouter, onError, onAuth);

            try {
                onResponse.accept(responseMessage);
            } catch (Throwable ignored) {
            }

            final byte[] responseBytes;
            try {
                responseBytes = serializer.serialize(responseMessage);
            } catch (Throwable e) {
                final var wrapped = e instanceof SerializationError
                        ? new TelepactError("telepact response serialization failed", "serialization", e)
                        : new TelepactError(
                                "telepact server processing failed while serializing the response",
                                "serialization",
                                e);
                try {
                    onError.accept(wrapped);
                } catch (Throwable ignored) {
                }

                final var unknownResponseBytes = serializer
                        .serialize(new Message(new HashMap<>(), Map.of("ErrorUnknown_", Map.of())));
                return new Response(unknownResponseBytes, Map.of());
            }
            return new Response(responseBytes, responseMessage.headers);
        } catch (Throwable e) {
            final var wrapped = e instanceof TelepactError
                    ? e
                    : e instanceof SerializationError
                            ? new TelepactError("telepact response serialization failed", "serialization", e)
                            : new TelepactError("telepact server processing failed", null, e);
            try {
                onError.accept(wrapped);
            } catch (Throwable ignored) {
            }

            final var responseBytes = serializer
                    .serialize(new Message(new HashMap<>(), Map.of("ErrorUnknown_", Map.of())));
            return new Response(responseBytes, Map.of());
        }
    }
}
