package io.github.brenbar.japi;

import java.util.concurrent.Future;
import java.util.function.BiFunction;
import java.util.function.Function;

/**
 * A jAPI client.
 */
public class Client {

    /**
     * A transport adapter that defines how Request/Response Messages are marshalled
     * to and from the transport.
     * 
     * <pre>
     * var transport = (requestMessage, serializer) -> {
     *     return CompletableFuture.supplyAsync(() -> {
     *         var requestMessageBytes = serializer.serialize(requestMessage);
     *         var responseMessageBytes = YOUR_TRANSPORT.transport(requestMessageBytes);
     *         responseMessage = serializer.deserialize(responseMessageBytes);
     *         return responseMessage;
     *     });
     * };
     * </pre>
     */
    interface Adapter extends BiFunction<Message, Serializer, Future<Message>> {
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

    public static class Options {
        Middleware middleware = (m, n) -> n.apply(m);
        boolean useBinaryDefault = false;
        boolean forceSendJsonDefault = true;
        boolean throwOnError = false;
        long timeoutMsDefault = 5000;
        SerializationImpl serializationImpl;

        /**
         * Set a new middleware for this client.
         * 
         * @param middleware
         * @return
         */
        public Options setMiddleware(Middleware middleware) {
            this.middleware = middleware;
            return this;
        }

        /**
         * Set if this client should use binary serialization for communication.
         * 
         * @param useBinary
         * @return
         */
        public Options setUseBinaryDefault(boolean useBinary) {
            this.useBinaryDefault = useBinary;
            return this;
        }

        /**
         * Set if this client should always send requests as JSON, even if receiving
         * responses as binary.
         * 
         * @param forceSendJson
         * @return
         */
        public Options setForceSendJsonDefault(boolean forceSendJson) {
            this.forceSendJsonDefault = forceSendJson;
            return this;
        }

        public Options setThrowOnError(boolean throwOnError) {
            this.throwOnError = throwOnError;
            return this;
        }

        /**
         * Set the default timeout for all requests.
         * 
         * @param timeoutMs
         * @return
         */
        public Options setTimeoutMsDefault(long timeoutMs) {
            this.timeoutMsDefault = timeoutMs;
            return this;
        }

        /**
         * Set an alternative serialization implementation.
         * 
         * @param serializer
         * @return
         */
        public Options setSerializationImpl(SerializationImpl serializationImpl) {
            this.serializationImpl = serializationImpl;
            return this;
        }
    }

    private Adapter adapter;
    private Serializer serializer;
    private Middleware middleware;
    private boolean useBinaryDefault;
    private boolean forceSendJsonDefault;
    private boolean throwOnError;
    private long timeoutMsDefault;

    /**
     * Create a client with the given transport adapter.
     * 
     * @param adapter
     */
    public Client(Adapter adapter, Options options) {
        this.adapter = adapter;

        this.middleware = options.middleware;
        this.useBinaryDefault = options.useBinaryDefault;
        this.forceSendJsonDefault = options.forceSendJsonDefault;
        this.throwOnError = options.throwOnError;
        this.timeoutMsDefault = options.timeoutMsDefault;

        this.serializer = new Serializer(new _DefaultSerializer(),
                new _ClientBinaryEncoder());
    }

    public Message createRequestMessage(Request request) {
        return _ClientUtil.constructRequestMessage(request, this.useBinaryDefault,
                this.forceSendJsonDefault, this.timeoutMsDefault);
    }

    /**
     * Submit a jAPI Request Message. Returns a jAPI Response Message.
     * 
     * @param request
     * @return
     */
    public Message send(Message requestMessage) {
        return this.middleware.apply(requestMessage, this::processMessage);
    }

    private Message processMessage(Message message) {
        return _ClientUtil.processRequestObject(message, this.adapter, this.serializer,
                this.timeoutMsDefault);
    }

}
