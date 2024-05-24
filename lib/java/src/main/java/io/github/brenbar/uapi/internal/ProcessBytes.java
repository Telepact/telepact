package io.github.brenbar.uapi.internal;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;

import io.github.brenbar.uapi.Message;
import io.github.brenbar.uapi.Serializer;
import io.github.brenbar.uapi.UApiSchema;

import static io.github.brenbar.uapi.internal.ParseRequestMessage.parseRequestMessage;
import static io.github.brenbar.uapi.internal.HandleMessage.handleMessage;

public class ProcessBytes {
    public static byte[] processBytes(byte[] requestMessageBytes, Serializer serializer, UApiSchema uApiSchema,
            Consumer<Throwable> onError, Consumer<Message> onRequest, Consumer<Message> onResponse,
            Function<Message, Message> handler) {
        try {
            final var requestMessage = parseRequestMessage(requestMessageBytes, serializer,
                    uApiSchema, onError);

            try {
                onRequest.accept(requestMessage);
            } catch (Throwable ignored) {
            }

            final var responseMessage = handleMessage(requestMessage, uApiSchema, handler, onError);

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
