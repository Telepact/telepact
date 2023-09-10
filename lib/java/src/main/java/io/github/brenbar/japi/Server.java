package io.github.brenbar.japi;

import java.util.*;
import java.util.function.BiFunction;
import java.util.function.Consumer;

/**
 * A jAPI Server.
 */
public class Server {

    /**
     * A Handler that defines how a jAPI Result is defined from the given
     * server context and jAPI Argument.
     * 
     * Example:
     * 
     * <pre>
     * var handler = (context, argument) -> {
     *     // TODO: Return a map compliant with your jAPI schema.
     *     return Map.of();
     * };
     * </pre>
     */
    interface Handler extends BiFunction<Context, Map<String, Object>, Map<String, Object>> {
    }

    JApiSchema jApiSchema;
    Handler handler;
    Consumer<Throwable> onError;
    BiFunction<Context, Map<String, Object>, Boolean> shouldValidateArgument;
    Serializer serializer;

    /**
     * Create a server with the given jAPI schema and handler.
     * 
     * @param jApiSchemaAsJson
     * @param handler
     */
    public Server(String jApiSchemaAsJson, Handler handler) {
        this.jApiSchema = InternalParse.newJApiSchemaWithInternalSchema(jApiSchemaAsJson);
        this.handler = handler;
        this.onError = (e) -> {
        };
        this.shouldValidateArgument = (c, a) -> true;

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

    public Server setShouldValidateArgument(BiFunction<Context, Map<String, Object>, Boolean> shouldValidateArgument) {
        this.shouldValidateArgument = shouldValidateArgument;
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
                    .serialize(List.of(responseMessage.headers, responseMessage.body));
        } catch (Exception e) {
            try {
                this.onError.accept(e);
            } catch (Exception ignored) {
            }
            return this.serializer
                    .serialize(List.of("fn._unknown", new HashMap<>(), Map.of("_errorUnknown", Map.of())));
        }
    }

    private Message processMessage(Message requestMessage) {
        return InternalServer.processMessage(requestMessage, this.jApiSchema, this.handler, this.shouldValidateArgument,
                this.onError);
    }
}
