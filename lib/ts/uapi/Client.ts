import { Callable, Awaitable } from 'concurrent.futures';
import { DefaultClientBinaryStrategy } from 'uapi/DefaultClientBinaryStrategy';
import { DefaultSerialization } from 'uapi/DefaultSerialization';
import { Serializer } from 'uapi/Serializer';
import { ClientBinaryEncoder } from 'uapi/internal/binary/ClientBinaryEncoder';
import { Message } from 'uapi/Message';
import { processRequestObject } from 'uapi/internal/ProcessRequestObject';

export class Client {
    private adapter: Callable<[Message, Serializer], Awaitable<Message>>;
    private useBinaryDefault: boolean;
    private timeoutMsDefault: number;
    private serializer: Serializer;

    constructor(adapter: Callable<[Message, Serializer], Awaitable<Message>>, options: Options) {
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

export class Options {
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
