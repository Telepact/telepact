import { Future } from 'java.util.concurrent';
import { BiFunction } from 'java.util.function';


/**
 * Options for the Client.
 */
export class Options {

    /**
     * Indicates if the client should use binary payloads instead of JSON.
     */
    public useBinary: boolean = false;

    /**
     * Indicates the default timeout that should be used if the _tim header is not
     * set.
     */
    public timeoutMsDefault: number = 5000;

    /**
     * The serialization implementation that should be used to serialize and
     * deserialize messages.
     */
    public serializationImpl: SerializationImpl = new _DefaultSerializer();

    /**
     * The client binary strategy that should be used to maintain binary
     * compatibility with the server.
     */
    public binaryStrategy: ClientBinaryStrategy = new _DefaultClientBinaryStrategy();
}


/**
 * A uAPI client.
 */
export class Client {

    private readonly adapter: BiFunction<Message, Serializer, Future<Message>>;
    private readonly serializer: Serializer;
    private readonly useBinaryDefault: boolean;
    private readonly timeoutMsDefault: number;

    /**
     * Create a client with the given transport adapter.
     * 
     * Example transport adapter:
     * 
     * <pre>
     * var adapter = (requestMessage, serializer) => {
     *     return CompletableFuture.supplyAsync(() => {
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
    constructor(adapter: BiFunction<Message, Serializer, Future<Message>>, options: Options) {
        this.adapter = adapter;
        this.useBinaryDefault = options.useBinary;
        this.timeoutMsDefault = options.timeoutMsDefault;
        this.serializer = new Serializer(options.serializationImpl,
            new _ClientBinaryEncoder(options.binaryStrategy));
    }

    /**
     * Submit a uAPI Request Message. Returns a uAPI Response Message.
     * 
     * @param request
     * @return
     */
    public request(requestMessage: Message): Message {
        return _Util.processRequestObject(requestMessage, this.adapter, this.serializer,
            this.timeoutMsDefault, this.useBinaryDefault);
    }
}