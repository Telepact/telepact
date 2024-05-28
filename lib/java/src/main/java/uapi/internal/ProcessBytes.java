package uapi.internal;

import static uapi.internal.HandleMessage.handleMessage;
import static uapi.internal.ParseRequestMessage.parseRequestMessage;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;

import uapi.Message;
import uapi.Serializer;
import uapi.UApiSchema;

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
