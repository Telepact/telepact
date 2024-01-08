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
        public Middleware middleware = (m, n) -> n.apply(m);
        public boolean useBinaryDefault = false;
        public boolean forceSendJsonDefault = true;
        public boolean throwOnError = false;
        public long timeoutMsDefault = 5000;
        public SerializationImpl serializationImpl = new _DefaultSerializer();
        public BinaryChecksumStrategy binaryChecksumStrategy = new _DefaultBinaryChecksumStrategy();
    }

    private Adapter adapter;
    private Serializer serializer;
    private Middleware middleware;
    private boolean useBinaryDefault;
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
        this.timeoutMsDefault = options.timeoutMsDefault;

        this.serializer = new Serializer(options.serializationImpl,
                new _ClientBinaryEncoder(options.binaryChecksumStrategy));
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
                this.timeoutMsDefault, this.useBinaryDefault);
    }

}
