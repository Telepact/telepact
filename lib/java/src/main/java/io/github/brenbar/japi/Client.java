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
     *         var requestMessageBytes = s.serialize(requestMessage);
     *         var responseMessageBytes = YOUR_TRANSPORT.transport(requestMessageBytes);
     *         responseMessage = s.deserialize(responseMessageBytes);
     *         return responseMessage;
     *     });
     * };
     * </pre>
     */
    interface Adapter extends BiFunction<Message, Marshaller, Future<Message>> {
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

    private Adapter adapter;
    private Marshaller serializer;
    private Middleware middleware;
    boolean useBinaryDefault;
    boolean forceSendJsonDefault;
    boolean throwOnError;
    long timeoutMsDefault;

    /**
     * Create a client with the given transport adapter.
     * 
     * @param adapter
     */
    public Client(Adapter adapter) {
        this.adapter = adapter;

        this.middleware = (m, n) -> n.apply(m);
        this.useBinaryDefault = false;
        this.forceSendJsonDefault = true;
        this.throwOnError = false;
        this.timeoutMsDefault = 5000;

        this.serializer = new Marshaller(new InternalDefaultSerializer(),
                new InternalClientBinaryEncoder());
    }

    /**
     * Set a new middleware for this client.
     * 
     * @param middleware
     * @return
     */
    public Client setMiddleware(Middleware middleware) {
        this.middleware = middleware;
        return this;
    }

    /**
     * Set if this client should use binary serialization for communication.
     * 
     * @param useBinary
     * @return
     */
    public Client setUseBinaryDefault(boolean useBinary) {
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
    public Client setForceSendJsonDefault(boolean forceSendJson) {
        this.forceSendJsonDefault = forceSendJson;
        return this;
    }

    public Client setThrowOnError(boolean throwOnError) {
        this.throwOnError = throwOnError;
        return this;
    }

    /**
     * Set the default timeout for all requests.
     * 
     * @param timeoutMs
     * @return
     */
    public Client setTimeoutMsDefault(long timeoutMs) {
        this.timeoutMsDefault = timeoutMs;
        return this;
    }

    /**
     * Set an alternative serialization implementation.
     * 
     * @param serializer
     * @return
     */
    public Client setSerializer(Serializer serializer) {
        this.serializer.serializer = serializer;
        return this;
    }

    public Message createRequestMessage(Request request) {
        return InternalClient.constructRequestMessage(request, useBinaryDefault,
                forceSendJsonDefault, timeoutMsDefault);
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
        return InternalClient.processRequestObject(message, this.adapter, this.serializer,
                this.timeoutMsDefault);
    }

}
