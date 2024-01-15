package io.github.brenbar.uapi;

import java.util.function.Consumer;
import java.util.function.Function;

/**
 * A uAPI Server.
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

    UApiSchema uApiSchema;
    Function<Message, Message> handler;
    Consumer<Throwable> onError;
    Consumer<Message> onRequest;
    Consumer<Message> onResponse;
    Serializer serializer;

    /**
     * Create a server with the given uAPI schema and handler.
     * 
     * @param uApiSchemaAsJson
     * @param handler
     */
    public Server(UApiSchema uApiSchema, Function<Message, Message> handler, Options options) {
        this.uApiSchema = uApiSchema;

        this.uApiSchema = UApiSchema.extend(uApiSchema, _InternalUApiUtil.getJson());

        this.handler = handler;

        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        var binaryEncoding = _SerializeUtil.constructBinaryEncoding(this.uApiSchema);
        var binaryEncoder = new _ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serializer, binaryEncoder);
    }

    /**
     * Process a given uAPI Request Message into a uAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] requestMessageBytes) {
        return _ServerUtil.processBytes(requestMessageBytes, this.serializer, this.uApiSchema, this.onError,
                this.onRequest, this.onResponse, this.handler);
    }
}
