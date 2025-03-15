import { MsgPactSchema } from './MsgPactSchema';
import { MockInvocation } from './internal/mock/MockInvocation';
import { MockStub } from './internal/mock/MockStub';
import { Server, ServerOptions as ServerOptions } from './Server';
import { RandomGenerator } from './RandomGenerator';
import { mockHandle } from './internal/mock/MockHandle';
import { MockMsgPactSchema } from './MockMsgPactSchema';

export class MockServer {
    /**
     * A Mock instance of a msgPact server.
     */

    constructor(mockMsgPactSchema: MockMsgPactSchema, options: MockServerOptions) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        this.stubs = [];
        this.invocations = [];

        const serverOptions = new ServerOptions();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        const msgPactSchema = new MsgPactSchema(
            mockMsgPactSchema.original,
            mockMsgPactSchema.full,
            mockMsgPactSchema.parsed,
            mockMsgPactSchema.parsedRequestHeaders,
            mockMsgPactSchema.parsedResponseHeaders,
        );

        this.server = new Server(msgPactSchema, this.handle, serverOptions);
    }

    private random: RandomGenerator;
    private enableGeneratedDefaultStub: boolean;
    private enableOptionalFieldGeneration: boolean;
    private randomizeOptionalFieldGeneration: boolean;
    private stubs: MockStub[];
    private invocations: MockInvocation[];
    private server: Server;

    async process(message: Uint8Array): Promise<Uint8Array> {
        /**
         * Process a given msgPact Request Message into a msgPact Response Message.
         *
         * @param message - The msgPact request message.
         * @returns The msgPact response message.
         */
        return await this.server.process(message);
    }

    private handle = async (requestMessage: any): Promise<any> => {
        return await mockHandle(
            requestMessage,
            this.stubs,
            this.invocations,
            this.random,
            this.server.msgPactSchema,
            this.enableGeneratedDefaultStub,
            this.enableOptionalFieldGeneration,
            this.randomizeOptionalFieldGeneration,
        );
    };
}

export class MockServerOptions {
    /**
     * Options for the MockServer.
     */

    onError: (error: Error) => void = (e) => {};
    enableMessageResponseGeneration = true;
    enableOptionalFieldGeneration = true;
    randomizeOptionalFieldGeneration = true;
    generatedCollectionLengthMin = 0;
    generatedCollectionLengthMax = 3;
}
