import { DefaultClientBinaryStrategy } from './DefaultClientBinaryStrategy';
import { DefaultSerialization } from './DefaultSerialization';
import { Serializer } from './Serializer';
import { ClientBinaryEncoder } from './internal/binary/ClientBinaryEncoder';
import { Message } from './Message';
import { processRequestObject } from './internal/ProcessRequestObject';

export class Client {
    private adapter: (message: Message, serializer: Serializer) => Promise<Message>;
    private useBinaryDefault: boolean;
    private timeoutMsDefault: number;
    private serializer: Serializer;

    constructor(adapter: (message: Message, serializer: Serializer) => Promise<Message>, options: ClientOptions) {
        this.adapter = adapter;
        this.useBinaryDefault = options.useBinary;
        this.timeoutMsDefault = options.timeoutMsDefault;
        this.serializer = new Serializer(options.serializationImpl, new ClientBinaryEncoder(options.binaryStrategy));
    }

    async request(requestMessage: Message): Promise<Message> {
        return await processRequestObject(
            requestMessage,
            this.adapter,
            this.serializer,
            this.timeoutMsDefault,
            this.useBinaryDefault,
        );
    }
}

export class ClientOptions {
    useBinary: boolean;
    timeoutMsDefault: number;
    serializationImpl: DefaultSerialization;
    binaryStrategy: DefaultClientBinaryStrategy;

    constructor() {
        this.useBinary = false;
        this.timeoutMsDefault = 5000;
        this.serializationImpl = new DefaultSerialization();
        this.binaryStrategy = new DefaultClientBinaryStrategy();
    }
}
