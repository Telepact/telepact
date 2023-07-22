package io.github.brenbar.japi;

import java.util.*;
import java.util.function.BiFunction;
import java.util.function.Consumer;
import java.util.function.Function;

/**
 * A jAPI Server.
 */
public class Server {

    /**
     * A Handler that defines how a jAPI Output is defined from the given
     * server context and jAPI Input.
     * 
     * Example:
     * 
     * <pre>
     * var handler = (context, input) -> {
     *     // TODO: Return a map compliant with your jAPI schema.
     *     return Map.of();
     * };
     * </pre>
     */
    interface Handler extends BiFunction<Context, Map<String, Object>, Map<String, Object>> {
    }

    /**
     * A Middleware layer that allows for customized Request/Response processing on
     * all requests.
     * 
     * Example:
     * 
     * <pre>
     * var middleware = (message, next) -> {
     *     // Custom logic here
     *     next.apply(message);
     * };
     * </pre>
     */
    interface Middleware extends BiFunction<Message, Function<Message, Message>, Message> {
    }

    JApiSchema jApiSchema;
    Handler handler;
    Middleware middleware;
    Consumer<Throwable> onError;
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
        this.middleware = (m, n) -> n.apply(m);

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
            try {
                var requestMessage = InternalServer.parseRequestMessage(requestMessageBytes, this.serializer,
                        this.jApiSchema);

                var responseMessage = this.middleware.apply(requestMessage, this::processMessage);

                return this.serializer
                        .serialize(List.of(responseMessage.target, responseMessage.headers, responseMessage.body));
            } catch (Exception e) {
                try {
                    this.onError.accept(e);
                } catch (Exception ignored) {
                }
                throw e;
            }
        } catch (InternalJApiError e) {
            return this.serializer.serialize(List.of(e.target, e.headers, e.body));
        } catch (Exception e) {
            return this.serializer.serialize(List.of("error._JApiFailure", new HashMap<>(), Map.of()));
        }
    }

    private Message processMessage(Message requestMessage) {
        return InternalServer.processMessage(requestMessage, this.jApiSchema, this.handler);
    }
}
