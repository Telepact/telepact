package io.github.brenbar.japi;

import java.util.*;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;

/**
 * A jAPI Server.
 */
public class Server {

    JApiSchema jApiSchema;
    Function<Message, Message> handler;
    Consumer<Throwable> onError;
    Serializer serializer;

    /**
     * Create a server with the given jAPI schema and handler.
     * 
     * @param jApiSchemaAsJson
     * @param handler
     */
    public Server(String jApiSchemaAsJson, Function<Message, Message> handler) {
        this.jApiSchema = InternalParse.newJApiSchemaWithInternalSchema(jApiSchemaAsJson);
        this.handler = handler;
        this.onError = (e) -> {
        };

        var binaryEncoder = InternalSerializer.constructBinaryEncoder(this.jApiSchema);
        var serializationStrategy = new InternalDefaultSerializationStrategy();
        var binaryEncodingStrategy = new InternalServerBinaryEncodingStrategy(binaryEncoder);
        this.serializer = new Serializer(serializationStrategy, binaryEncodingStrategy);
    }

    /**
     * Set an error handler to run on every error that occurs during request
     * processing.
     * 
     * @param onError
     * @return
     */
    public Server setOnError(Consumer<Throwable> onError) {
        this.onError = onError;
        return this;
    }

    /**
     * Set an alternative serialization implementation.
     * 
     * @param strategy
     * @return
     */
    public Server setSerializationStrategy(SerializationStrategy strategy) {
        this.serializer.serializationStrategy = strategy;
        return this;
    }

    /**
     * Process a given jAPI Request Message into a jAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] requestMessageBytes) {
        return deserializeAndProcess(requestMessageBytes);
    }

    private byte[] deserializeAndProcess(byte[] requestMessageBytes) {
        try {
            var requestMessage = InternalServer.parseRequestMessage(requestMessageBytes, this.serializer,
                    this.jApiSchema, this.onError);

            var responseMessage = processMessage(requestMessage);

            return this.serializer
                    .serialize(List.of(responseMessage.header, responseMessage.body));
        } catch (Exception e) {
            try {
                this.onError.accept(e);
            } catch (Exception ignored) {
            }
            return this.serializer
                    .serialize(List.of(new HashMap<>(), Map.of("_errorUnknown", Map.of())));
        }
    }

    private Message processMessage(Message requestMessage) {
        return InternalServer.processMessage(requestMessage, this.jApiSchema, this.handler,
                this.onError);
    }
}
