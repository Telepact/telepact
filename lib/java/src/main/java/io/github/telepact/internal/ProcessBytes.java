//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal;

import static io.github.telepact.internal.HandleMessage.handleMessage;
import static io.github.telepact.internal.ParseRequestMessage.parseRequestMessage;
import static io.github.telepact.internal.UnknownError.buildUnknownErrorMessage;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;

import io.github.telepact.FunctionRouter;
import io.github.telepact.Message;
import io.github.telepact.Response;
import io.github.telepact.SerializationError;
import io.github.telepact.TelepactError;
import io.github.telepact.TelepactSchema;
import io.github.telepact.Serializer;
import io.github.telepact.Server.AuthHandler;
import io.github.telepact.Server.Middleware;

public class ProcessBytes {
    public static Response processBytes(byte[] requestMessageBytes, Consumer<Map<String, Object>> updateHeaders, Serializer serializer, TelepactSchema telepactSchema,
            Consumer<TelepactError> onError, Consumer<Message> onRequest, Consumer<Message> onResponse,
            AuthHandler onAuth,
            Middleware middleware, FunctionRouter functionRouter) {
        try {
            final var requestMessage = parseRequestMessage(requestMessageBytes, serializer,
                    telepactSchema, onError);

            try {
                onRequest.accept(requestMessage);
            } catch (Throwable ignored) {
            }

            final var responseMessage = handleMessage(requestMessage, updateHeaders, telepactSchema, middleware, functionRouter, onError, onAuth);

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
                        .serialize(buildUnknownErrorMessage(wrapped, new HashMap<>()));
                return new Response(unknownResponseBytes, Map.of());
            }
            return new Response(responseBytes, responseMessage.headers);
        } catch (Throwable e) {
            final TelepactError wrapped = e instanceof TelepactError telepactError
                    ? telepactError
                    : e instanceof SerializationError
                            ? new TelepactError("telepact response serialization failed", "serialization", e)
                            : new TelepactError("telepact server processing failed", null, e);
            try {
                onError.accept(wrapped);
            } catch (Throwable ignored) {
            }

            final var responseBytes = serializer
                    .serialize(buildUnknownErrorMessage(wrapped, new HashMap<>()));
            return new Response(responseBytes, Map.of());
        }
    }
}
