package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Consumer;
import java.util.function.Function;

/**
 * A uAPI Server.
 */
public class Server {

    /**
     * Options for the Server.
     */
    public static class Options {

        /**
         * Handler for errors thrown during message processing.
         */
        public Consumer<Throwable> onError = (e) -> {
        };

        /**
         * Execution hook that runs when a request Message is received.
         */
        public Consumer<Message> onRequest = (m) -> {
        };

        /**
         * Execution hook that runs when a response Message is about to be returned.
         */
        public Consumer<Message> onResponse = (m) -> {
        };

        /**
         * Flag to indicate if authentication via the _auth header is required.
         */
        public boolean authRequired = true;

        /**
         * The serialization implementation that should be used to serialize and
         * deserialize messages.
         */
        public SerializationImpl serializer = new _DefaultSerializer();
    }

    final UApiSchema uApiSchema;
    private final Function<Message, Message> handler;
    private final Consumer<Throwable> onError;
    private final Consumer<Message> onRequest;
    private final Consumer<Message> onResponse;
    private final Serializer serializer;

    /**
     * Create a server with the given uAPI schema and handler.
     * 
     * @param uApiSchemaAsJson
     * @param handler
     */
    public Server(UApiSchema uApiSchema, Function<Message, Message> handler, Options options) {
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        final Map<String, _UType> parsedTypes = new HashMap<>();
        final Map<String, _UType> typeExtensions = new HashMap<>();

        typeExtensions.put("_ext._Select", new _USelect(parsedTypes));

        this.uApiSchema = UApiSchema.extendWithExtensions(uApiSchema, _Util.getInternalUApiJson(), typeExtensions);

        parsedTypes.putAll(this.uApiSchema.parsed);

        final var binaryEncoding = _Util.constructBinaryEncoding(this.uApiSchema);
        final var binaryEncoder = new _ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serializer, binaryEncoder);

        if (((_UStruct) this.uApiSchema.parsed.get("struct._Auth")).fields.size() == 0 && options.authRequired) {
            throw new RuntimeException(
                    "Unauthenticated server. Either define a non-empty `struct._Auth` in your schema or set `options.authRequired` to `false`.");
        }
    }

    /**
     * Process a given uAPI Request Message into a uAPI Response Message.
     * 
     * @param requestMessageBytes
     * @return
     */
    public byte[] process(byte[] requestMessageBytes) {
        return _Util.processBytes(requestMessageBytes, this.serializer, this.uApiSchema, this.onError,
                this.onRequest, this.onResponse, this.handler);
    }
}
