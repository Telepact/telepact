import { UApiSchema } from 'uapi/UApiSchema';
import { MockInvocation } from 'uapi/internal/mock/MockInvocation';
import { MockStub } from 'uapi/internal/mock/MockStub';
import { UType } from 'uapi/internal/types/UType';
import { extendUApiSchema } from 'uapi/internal/schema/ExtendUApiSchema';
import { getMockUApiJson } from 'uapi/internal/schema/GetMockUApiJson';
import { Server } from 'uapi/Server';
import { RandomGenerator } from 'uapi/RandomGenerator';
import { UMockCall } from 'uapi/internal/types/UMockCall';
import { UMockStub } from 'uapi/internal/types/UMockStub';
import { mockHandle } from 'uapi/internal/mock/MockHandle';

export class MockServer {
    /**
     * A Mock instance of a uAPI server.
     */

    constructor(
        private uApiSchema: UApiSchema,
        private options: Options,
    ) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        this.stubs = [];
        this.invocations = [];

        const parsedTypes: { [key: string]: UType } = {};
        const typeExtensions: { [key: string]: UType } = {};

        typeExtensions['_ext.Call_'] = new UMockCall(parsedTypes);
        typeExtensions['_ext.Stub_'] = new UMockStub(parsedTypes);

        const combinedUApiSchema: UApiSchema = extendUApiSchema(uApiSchema, getMockUApiJson(), typeExtensions);

        const serverOptions = new Server.Options();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        this.server = new Server(combinedUApiSchema, this.handle, serverOptions);

        const finalUApiSchema: UApiSchema = this.server.uApiSchema;
        const finalParsedUApiSchema = finalUApiSchema.parsed;

        Object.assign(parsedTypes, finalParsedUApiSchema);
    }

    private random: RandomGenerator;
    private enableGeneratedDefaultStub: boolean;
    private enableOptionalFieldGeneration: boolean;
    private randomizeOptionalFieldGeneration: boolean;
    private stubs: MockStub[];
    private invocations: MockInvocation[];
    private server: Server;

    async process(message: Buffer): Promise<Buffer> {
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

export class Options {
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
