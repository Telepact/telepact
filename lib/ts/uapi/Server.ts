import { DefaultSerialization } from 'uapi/DefaultSerialization';
import { Serializer } from 'uapi/Serializer';
import { ServerBinaryEncoder } from 'uapi/internal/binary/ServerBinaryEncoder';
import { USelect } from 'uapi/internal/types/USelect';
import { Message } from 'uapi/Message';
import { UApiSchema } from 'uapi/UApiSchema';
import { UType } from 'uapi/internal/types/UType';
import { constructBinaryEncoding } from 'uapi/internal/binary/ConstructBinaryEncoding';
import { extendUapiSchema } from 'uapi/internal/schema/ExtendUApiSchema';
import { getInternalUApiJson } from 'uapi/internal/schema/GetInternalUApiJson';
import { UStruct } from 'uapi/internal/types/UStruct';
import { processBytes } from 'uapi/internal/ProcessBytes';

export class Server {
    handler: (message: Message) => Promise<Message>;
    onError: (error: any) => void;
    onRequest: (message: Message) => void;
    onResponse: (message: Message) => void;
    uApiSchema: UApiSchema;
    serializer: Serializer;

    constructor(uApiSchema: UApiSchema, handler: (message: Message) => Promise<Message>, options: Options) {
        this.handler = handler;
        this.onError = options.onError;
        this.onRequest = options.onRequest;
        this.onResponse = options.onResponse;

        const parsedTypes: { [key: string]: UType } = {};
        const typeExtensions: { [key: string]: UType } = {
            '_ext.Select_': new USelect(parsedTypes),
        };

        this.uApiSchema = extendUapiSchema(uApiSchema, getInternalUApiJson(), typeExtensions);

        Object.assign(parsedTypes, this.uApiSchema.parsed);

        const binaryEncoding = constructBinaryEncoding(this.uApiSchema);
        const binaryEncoder = new ServerBinaryEncoder(binaryEncoding);
        this.serializer = new Serializer(options.serialization, binaryEncoder);

        if (
            Object.keys((this.uApiSchema.parsed['struct.Auth_'] as UStruct).fields).length === 0 &&
            options.authRequired
        ) {
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

export class Options {
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
