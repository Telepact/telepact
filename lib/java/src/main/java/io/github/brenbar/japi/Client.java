package io.github.brenbar.japi;

import java.util.List;
import java.util.Map;
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
    interface Adapter extends BiFunction<List<Object>, Serializer, Future<List<Object>>> {
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
    interface Middleware extends BiFunction<List<Object>, Function<List<Object>, List<Object>>, List<Object>> {
    }

    private Adapter adapter;
    private Serializer serializer;
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

        this.serializer = new Serializer(new InternalDefaultSerializationStrategy(),
                new InternalClientBinaryEncodingStrategy());
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
     * @param serializationStrategy
     * @return
     */
    public Client setSerializationStrategy(SerializationStrategy serializationStrategy) {
        this.serializer.serializationStrategy = serializationStrategy;
        return this;
    }

    /**
     * Submit a jAPI Request Message. Returns a jAPI Response Message Body or throws
     * jAPI error.
     * 
     * @param request
     * @return
     */
    public Map<String, Object> submit(
            Request request) {

        var requestMessage = InternalClient.constructRequestMessage(request, useBinaryDefault,
                forceSendJsonDefault, timeoutMsDefault);

        var response = this.middleware.apply(requestMessage, this::processMessage);

        var responseMessageType = (String) response.get(0);
        var result = (Map<String, Object>) response.get(2);

        if (throwOnError && result.containsKey("err")) {
            throw new JApiError(result);
        }

        return result;
    }

    private List<Object> processMessage(List<Object> message) {
        return InternalClient.processRequestObject(message, this.adapter, this.serializer,
                this.timeoutMsDefault);
    }

}
