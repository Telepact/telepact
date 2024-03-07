import { _RandomGenerator } from "./_RandomGenerator";
import { Message } from "./Message";
import { Server, ServerOptions } from "./Server";
import { UApiSchema } from "./UApiSchema";
import { getMockUApiJson, mockHandle } from "./_util";
import { _MockInvocation, _MockStub, _UMockCall, _UMockStub } from "./_utilTypes";


/**
 * Options for the MockServer.
 */
export class MockServerOptions {
    /**
     * Handler for errors thrown during message processing.
     */
    onError: (error: Error) => void = (e) => {};

    /**
     * Flag to indicate if message responses should be randomly generated when no stub is available.
     */
    enableMessageResponseGeneration: boolean = true;

    /**
     * Minimum length for randomly generated arrays and objects.
     */
    generatedCollectionLengthMin: number = 0;

    /**
     * Maximum length for randomly generated arrays and objects.
     */
    generatedCollectionLengthMax: number = 3;
}

/**
 * Create a mock server with the given uAPI Schema.
 * 
 * @param uApiSchema 
 * @param options 
 */
export class MockServer {
    private server: Server;
    private random: _RandomGenerator;
    private enableGeneratedDefaultStub: boolean;
    private stubs: _MockStub[] = [];
    private invocations: _MockInvocation[] = [];

    constructor(uApiSchema: UApiSchema, options: MockServerOptions) {
        this.random = new _RandomGenerator(options.generatedCollectionLengthMin || 0, options.generatedCollectionLengthMax || 3);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration !== undefined ? options.enableMessageResponseGeneration : true;

        const parsedTypes: Record<string, any> = {};
        const typeExtensions: Record<string, any> = {};

        typeExtensions['_ext._Call'] = new _UMockCall(parsedTypes);
        typeExtensions['_ext._Stub'] = new _UMockStub(parsedTypes);

        const combinedUApiSchema = UApiSchema.extendWithExtensions(uApiSchema, getMockUApiJson(), typeExtensions);

        const serverOptions: ServerOptions = new ServerOptions();
        serverOptions.onError = options.onError;

        this.server = new Server(combinedUApiSchema, this.handle.bind(this), serverOptions);

        const finalParsedUApiSchema = this.server.uApiSchema.parsed;
        Object.assign(parsedTypes, finalParsedUApiSchema);
    }

    /**
     * Process a given uAPI Request Message into a uAPI Response Message.
     * 
     * @param message 
     * @returns 
     */
    public async process(message: Uint8Array): Promise<Uint8Array> {
        return this.server.process(message);
    }

    private async handle(requestMessage: Message): Promise<Message> {
        return mockHandle(requestMessage, this.stubs, this.invocations, this.random, this.server.uApiSchema, this.enableGeneratedDefaultStub);
    }
}