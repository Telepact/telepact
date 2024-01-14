package io.github.brenbar.japi;

import java.util.concurrent.Future;
import java.util.function.BiFunction;

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

    public static class Options {
        public boolean useBinaryDefault = false;
        public long timeoutMsDefault = 5000;
        public SerializationImpl serializationImpl = new _DefaultSerializer();
        public BinaryChecksumStrategy binaryChecksumStrategy = new _DefaultBinaryChecksumStrategy();
    }

    private Adapter adapter;
    private Serializer serializer;
    private boolean useBinaryDefault;
    private long timeoutMsDefault;

    /**
     * Create a client with the given transport adapter.
     * 
     * @param adapter
     */
    public Client(Adapter adapter, Options options) {
        this.adapter = adapter;

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
        return _ClientUtil.processRequestObject(requestMessage, this.adapter, this.serializer,
                this.timeoutMsDefault, this.useBinaryDefault);
    }

}
