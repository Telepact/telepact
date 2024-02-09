import { SerializationImpl } from './SerializationImpl';
import { _DefaultSerializationImpl } from './_DefaultSerializationImpl';
import { _DefaultClientBinaryStrategy } from './_DefaultClientBinaryStrategy';
import { Message } from './Message';
import { Serializer } from './Serializer';
import { _ClientBinaryEncoder } from './_utilTypes';
import { processRequestObject } from './_util';


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
    public serializationImpl: SerializationImpl = new _DefaultSerializationImpl();

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

    private readonly adapter: (m: Message, s: Serializer) => Promise<Message>;
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
    constructor(adapter: (m: Message, s: Serializer) => Promise<Message>, options: Options) {
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
    public async request(requestMessage: Message): Promise<Message> {
        return processRequestObject(requestMessage, this.adapter, this.serializer,
            this.timeoutMsDefault, this.useBinaryDefault);
    }
}