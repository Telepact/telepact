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
        public SerializationImpl serializer = new InternalDefaultSerializer();

        public Options setOnError(Consumer<Throwable> onError) {
            this.onError = onError;
            return this;
        }

        public Options setSerializer(SerializationImpl serializer) {
            this.serializer = serializer;
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
    public Server(JApiSchema jApiSchema, Function<Message, Message> handler, Options options) {
        var internalJApiSchema = new JApiSchema(InternalJApi.getJson());
        this.jApiSchema = new JApiSchema(jApiSchema, internalJApiSchema);
        this.handler = handler;

        this.onError = options.onError;

        var binaryEncoding = InternalSerializer.constructBinaryEncoding(this.jApiSchema);
        var binaryEncoder = new InternalServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serializer, binaryEncoder);
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
