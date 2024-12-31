import { DefaultSerialization } from './DefaultSerialization';
import { Serializer } from './Serializer';
import { ServerBinaryEncoder } from './internal/binary/ServerBinaryEncoder';
import { Message } from './Message';
import { UApiSchema } from './UApiSchema';
import { constructBinaryEncoding } from './internal/binary/ConstructBinaryEncoding';
import { processBytes } from './internal/ProcessBytes';

export class Server {
    handler: (message: Message) => Promise<Message>;
    onError: (error: any) => void;
    onRequest: (message: Message) => void;
    onResponse: (message: Message) => void;
    uApiSchema: UApiSchema;
    serializer: Serializer;

    constructor(uApiSchema: UApiSchema, handler: (message: Message) => Promise<Message>, options: ServerOptions) {
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        this.uApiSchema = uApiSchema;

        const binaryEncoding = constructBinaryEncoding(this.uApiSchema);
        const binaryEncoder = new ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serialization, binaryEncoder);

        if (!('struct.Auth_' in this.uApiSchema.parsed) && options.authRequired) {
            throw new Error(
                'Unauthenticated server. Either define a non-empty `struct._Auth` in your schema or set `options.authRequired` to `false`.',
            );
        }
    }

    async process(requestMessageBytes: Uint8Array): Promise<Uint8Array> {
        return await processBytes(
            requestMessageBytes,
            this.serializer,
            this.uApiSchema,
            this.onError,
            this.onRequest,
            this.onResponse,
            this.handler,
        );
    }
}

export class ServerOptions {
    onError: (error: any) => void;
    onRequest: (message: Message) => void;
    onResponse: (message: Message) => void;
    authRequired: boolean;
    serialization: DefaultSerialization;

    constructor() {
        this.onError = (e: any) => {};
        this.onRequest = (m: Message) => {};
        this.onResponse = (m: Message) => {};
        this.authRequired = true;
        this.serialization = new DefaultSerialization();
    }
}
