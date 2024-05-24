package io.github.brenbar.uapi;

import java.util.concurrent.Future;
import java.util.function.BiFunction;

import io.github.brenbar.uapi.internal.binary.ClientBinaryEncoder;

import static io.github.brenbar.uapi.internal.ProcessRequestObject.processRequestObject;

/**
 * A uAPI client.
 */
public class Client {

    /**
     * Options for the Client.
     */
    public static class Options {

        /**
         * Indicates if the client should use binary payloads instead of JSON.
         */
        public boolean useBinary = false;

        /**
         * Indicates the default timeout that should be used if the _tim header is not
         * set.
         */
        public long timeoutMsDefault = 5000;

        /**
         * The serialization implementation that should be used to serialize and
         * deserialize messages.
         */
        public SerializationImpl serializationImpl = new DefaultSerializer();

        /**
         * The client binary strategy that should be used to maintain binary
         * compatibility with the server.
         */
        public ClientBinaryStrategy binaryStrategy = new DefaultClientBinaryStrategy();
    }

    private final BiFunction<Message, Serializer, Future<Message>> adapter;
    private final Serializer serializer;
    private final boolean useBinaryDefault;
    private final long timeoutMsDefault;

    /**
     * Create a client with the given transport adapter.
     * 
     * Example transport adapter:
     * 
     * <pre>
     * var adapter = (requestMessage, serializer) -> {
     *     return CompletableFuture.supplyAsync(() -> {
     *         var requestMessageBytes = serializer.serialize(requestMessage);
     *         var responseMessageBytes = YOUR_TRANSPORT.transport(requestMessageBytes);
     *         responseMessage = serializer.deserialize(responseMessageBytes);
     *         return responseMessage;
     *     });
     * };
     * </pre>
     * 
     * @param adapter
     */
    public Client(BiFunction<Message, Serializer, Future<Message>> adapter, Options options) {
        this.adapter = adapter;
        this.useBinaryDefault = options.useBinary;
        this.timeoutMsDefault = options.timeoutMsDefault;
        this.serializer = new Serializer(options.serializationImpl,
                new ClientBinaryEncoder(options.binaryStrategy));
    }

    /**
     * Submit a uAPI Request Message. Returns a uAPI Response Message.
     * 
     * @param request
     * @return
     */
    public Message request(Message requestMessage) {
        return processRequestObject(requestMessage, this.adapter, this.serializer,
                this.timeoutMsDefault, this.useBinaryDefault);
    }

}
