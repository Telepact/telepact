import { Message } from "./Message";
import { SerializationImpl } from "./SerializationImpl";
import { Serializer } from "./Serializer";
import { UApiSchema } from "./UApiSchema";
import { _DefaultSerializationImpl } from "./_DefaultSerializationImpl";
import { constructBinaryEncoding, getInternalUApiJson, processBytes } from "./_util";
import { _ServerBinaryEncoder } from "./_utilTypes";

/**
 * Options for the Server.
 */
export class Options {
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
    private readonly handler: (message: Message) => Message;
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
    constructor(uApiSchema: UApiSchema, handler: (message: Message) => Message, options: Options) {
        this.uApiSchema = UApiSchema.extend(uApiSchema, getInternalUApiJson());
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        const binaryEncoding = constructBinaryEncoding(this.uApiSchema);
        const binaryEncoder = new _ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serializer, binaryEncoder);
    }

    /**
     * Process a given uAPI Request Message into a uAPI Response Message.
     * 
     * @param requestMessageBytes 
     * @returns 
     */
    process(requestMessageBytes: Uint8Array): Uint8Array {
        return processBytes(requestMessageBytes, this.serializer, this.uApiSchema, this.onError,
            this.onRequest, this.onResponse, this.handler);
    }
}