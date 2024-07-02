import { UApiSchema } from './UApiSchema';
import { MockInvocation } from './internal/mock/MockInvocation';
import { MockStub } from './internal/mock/MockStub';
import { UType } from './internal/types/UType';
import { extendUapiSchema } from './internal/schema/ExtendUApiSchema';
import { getMockUApiJson } from './internal/schema/GetMockUApiJson';
import { Server, ServerOptions as ServerOptions } from './Server';
import { RandomGenerator } from './RandomGenerator';
import { UMockCall } from './internal/types/UMockCall';
import { UMockStub } from './internal/types/UMockStub';
import { mockHandle } from './internal/mock/MockHandle';

export class MockServer {
    /**
     * A Mock instance of a uAPI server.
     */

    constructor(
        private uApiSchema: UApiSchema,
        private options: MockServerOptions,
    ) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        this.stubs = [];
        this.invocations = [];

        const combinedUApiSchema: UApiSchema = extendUapiSchema(uApiSchema, getMockUApiJson());

        const serverOptions = new ServerOptions();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        this.server = new Server(combinedUApiSchema, this.handle, serverOptions);
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
         * Process a given uAPI Request Message into a uAPI Response Message.
         *
         * @param message - The uAPI request message.
         * @returns The uAPI response message.
         */
        return await this.server.process(message);
    }

    private handle = async (requestMessage: any): Promise<any> => {
        return await mockHandle(
            requestMessage,
            this.stubs,
            this.invocations,
            this.random,
            this.server.uApiSchema,
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
