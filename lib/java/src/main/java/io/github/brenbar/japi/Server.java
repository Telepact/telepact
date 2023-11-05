package io.github.brenbar.japi;

import java.util.*;
import java.util.function.Consumer;
import java.util.function.Function;

/**
 * A jAPI Server.
 */
public class Server {

    public static class Options {
        public Consumer<Throwable> onError = (e) -> {
        };
        public SerializationStrategy serializationStrategy = new InternalDefaultSerializationStrategy();
        public Map<String, TypeExtension> typeExtensions = new HashMap<>();

        public Options setOnError(Consumer<Throwable> onError) {
            this.onError = onError;
            return this;
        }

        public Options setSerializationStrategy(SerializationStrategy serializationStrategy) {
            this.serializationStrategy = serializationStrategy;
            return this;
        }

        public Options setTypeExtensions(Map<String, TypeExtension> typeExtensions) {
            this.typeExtensions = typeExtensions;
            return this;
        }
    }

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
    public Server(String jApiSchemaAsJson, Function<Message, Message> handler, Options options) {
        this.jApiSchema = InternalParse.newJApiSchemaWithInternalSchema(jApiSchemaAsJson, options.typeExtensions);
        this.handler = handler;

        this.onError = options.onError;

        var binaryEncoder = InternalSerializer.constructBinaryEncoder(this.jApiSchema);
        var binaryEncodingStrategy = new InternalServerBinaryEncodingStrategy(binaryEncoder);
        this.serializer = new Serializer(options.serializationStrategy, binaryEncodingStrategy);
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

            return this.serializer.serialize(responseMessage);
        } catch (Exception e) {
            try {
                this.onError.accept(e);
            } catch (Exception ignored) {
            }
            return this.serializer
                    .serialize(new Message(new HashMap<>(), Map.of("_errorUnknown", Map.of())));
        }
    }

    private Message processMessage(Message requestMessage) {
        return InternalServer.processMessage(requestMessage, this.jApiSchema, this.handler,
                this.onError);
    }
}
