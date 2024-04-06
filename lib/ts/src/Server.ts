import { Message } from './Message';
import { SerializationImpl } from './SerializationImpl';
import { Serializer } from './Serializer';
import { UApiSchema } from './UApiSchema';
import { _DefaultSerializationImpl } from './_DefaultSerializationImpl';
import { constructBinaryEncoding, extendUApiSchema, getInternalUApiJson, processBytes } from './_util';
import { _ServerBinaryEncoder, _USelect, _UStruct, _UType } from './_utilTypes';

/**
 * Options for the Server.
 */
export class ServerOptions {
    /**
     * Handler for errors thrown during message processing.
     */
    onError: (error: Error) => void = (e: Error) => {};

    /**
     * Execution hook that runs when a request Message is received.
     */
    onRequest: (message: Message) => void = (m: Message) => {};

    /**
     * Execution hook that runs when a response Message is about to be returned.
     */
    onResponse: (message: Message) => void = (m: Message) => {};

    /**
     * Flag to indicate if authentication via the _auth header is required.
     */
    authRequired: boolean = true;

    /**
     * The serialization implementation that should be used to serialize and
     * deserialize messages.
     */
    serializer: SerializationImpl = new _DefaultSerializationImpl();
}

/**
 * A uAPI Server.
 */
export class Server {
    readonly uApiSchema: UApiSchema;
    private readonly handler: (message: Message) => Promise<Message>;
    private readonly onError: (error: Error) => void;
    private readonly onRequest: (message: Message) => void;
    private readonly onResponse: (message: Message) => void;
    private readonly serializer: Serializer;

    /**
     * Create a server with the given uAPI schema and handler.
     *
     * @param uApiSchema
     * @param handler
     * @param options
     */
    constructor(uApiSchema: UApiSchema, handler: (message: Message) => Promise<Message>, options: ServerOptions) {
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        const parsedTypes: Record<string, _UType> = {};
        const typeExtensions: Record<string, _UType> = {};

        typeExtensions['_ext.Select_'] = new _USelect(parsedTypes);

        this.uApiSchema = extendUApiSchema(uApiSchema, getInternalUApiJson(), typeExtensions);

        Object.assign(parsedTypes, this.uApiSchema.parsed);

        const binaryEncoding = constructBinaryEncoding(this.uApiSchema);
        const binaryEncoder = new _ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serializer, binaryEncoder);

        if (
            Object.keys((this.uApiSchema.parsed['struct.Auth_'] as _UStruct).fields).length === 0 &&
            options.authRequired
        ) {
            throw Error(
                'Unauthenticated server. Either define a non-empty `struct._Auth` in your schema or set `options.authRequired` to `false`.'
            );
        }
    }

    /**
     * Process a given uAPI Request Message into a uAPI Response Message.
     *
     * @param requestMessageBytes
     * @returns
     */
    public async process(requestMessageBytes: Uint8Array): Promise<Uint8Array> {
        return processBytes(
            requestMessageBytes,
            this.serializer,
            this.uApiSchema,
            this.onError,
            this.onRequest,
            this.onResponse,
            this.handler
        );
    }
}
