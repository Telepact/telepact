package io.github.msgpact.internal;

import static io.github.msgpact.internal.HandleMessage.handleMessage;
import static io.github.msgpact.internal.ParseRequestMessage.parseRequestMessage;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;

import io.github.msgpact.Message;
import io.github.msgpact.MsgPactSchema;
import io.github.msgpact.Serializer;

public class ProcessBytes {
    public static byte[] processBytes(byte[] requestMessageBytes, Serializer serializer, MsgPactSchema msgPactSchema,
            Consumer<Throwable> onError, Consumer<Message> onRequest, Consumer<Message> onResponse,
            Function<Message, Message> handler) {
        try {
            final var requestMessage = parseRequestMessage(requestMessageBytes, serializer,
                    msgPactSchema, onError);

            try {
                onRequest.accept(requestMessage);
            } catch (Throwable ignored) {
            }

            final var responseMessage = handleMessage(requestMessage, msgPactSchema, handler, onError);

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
