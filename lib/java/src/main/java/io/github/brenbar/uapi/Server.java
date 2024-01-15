package io.github.brenbar.uapi;

import java.util.function.Consumer;
import java.util.function.Function;

/**
 * A jAPI Server.
 */
public class Server {

    public static class Options {
        public Consumer<Throwable> onError = (e) -> {
        };
        public Consumer<Message> onRequest = (m) -> {
        };
        public Consumer<Message> onResponse = (m) -> {
        };
        public SerializationImpl serializer = new _DefaultSerializer();

        public Options setOnError(Consumer<Throwable> onError) {
            this.onError = onError;
            return this;
        }

        public Options setOnRequest(Consumer<Message> onRequest) {
            this.onRequest = onRequest;
            return this;
        }

        public Options setOnResponse(Consumer<Message> onResponse) {
            this.onResponse = onResponse;
            return this;
        }

        public Options setSerializer(SerializationImpl serializer) {
            this.serializer = serializer;
            return this;
        }
    }

    UApiSchema jApiSchema;
    Function<Message, Message> handler;
    Consumer<Throwable> onError;
    Consumer<Message> onRequest;
    Consumer<Message> onResponse;
    Serializer serializer;

    /**
     * Create a server with the given jAPI schema and handler.
     * 
     * @param jApiSchemaAsJson
     * @param handler
     */
    public Server(UApiSchema jApiSchema, Function<Message, Message> handler, Options options) {
        this.jApiSchema = jApiSchema;

        this.jApiSchema = UApiSchema.extend(jApiSchema, _InternalUApiUtil.getJson());

        this.handler = handler;

        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        var binaryEncoding = _SerializeUtil.constructBinaryEncoding(this.jApiSchema);
        var binaryEncoder = new _ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serializer, binaryEncoder);
    }

    /**
     * Process a given jAPI Request Message into a jAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] requestMessageBytes) {
        return _ServerUtil.processBytes(requestMessageBytes, this.serializer, this.jApiSchema, this.onError,
                this.onRequest, this.onResponse, this.handler);
    }
}
