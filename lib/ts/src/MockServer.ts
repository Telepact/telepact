//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

import { TelepactSchema } from './TelepactSchema.js';
import { MockInvocation } from './internal/mock/MockInvocation.js';
import { MockStub } from './internal/mock/MockStub.js';
import { FunctionRouter, FunctionRoutes, Server, ServerOptions as ServerOptions } from './Server.js';
import { RandomGenerator } from './RandomGenerator.js';
import {
    handleAutoMockFunction,
    handleClearCalls,
    handleClearStubs,
    handleCreateStub,
    handleSetRandomSeed,
    handleVerify,
    handleVerifyNoMoreInteractions,
} from './internal/mock/MockHandle.js';
import { MockTelepactSchema } from './MockTelepactSchema.js';
import { Response } from './Response.js';

export class MockServer {
    /**
     * A Mock instance of a telepact server.
     */

    constructor(mockTelepactSchema: MockTelepactSchema, options: MockServerOptions) {
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
        this.enableGeneratedDefaultStub = options.enableMessageResponseGeneration;
        this.enableOptionalFieldGeneration = options.enableOptionalFieldGeneration;
        this.randomizeOptionalFieldGeneration = options.randomizeOptionalFieldGeneration;

        this.stubs = [];
        this.invocations = [];

        const serverOptions = new ServerOptions();
        serverOptions.onError = options.onError;
        serverOptions.authRequired = false;

        const telepactSchema = new TelepactSchema(
            mockTelepactSchema.original,
            mockTelepactSchema.full,
            mockTelepactSchema.parsed,
            mockTelepactSchema.parsedRequestHeaders,
            mockTelepactSchema.parsedResponseHeaders,
        );

        const functionRouter = new FunctionRouter(this.createFunctionRoutes(telepactSchema));
        this.server = new Server(telepactSchema, functionRouter, serverOptions);
    }

    private random: RandomGenerator;
    private enableGeneratedDefaultStub: boolean;
    private enableOptionalFieldGeneration: boolean;
    private randomizeOptionalFieldGeneration: boolean;
    private stubs: MockStub[];
    private invocations: MockInvocation[];
    private server: Server;

    async process(message: Uint8Array): Promise<Response> {
        /**
         * Process a given telepact Request Message into a telepact Response Message.
         *
         * @param message - The telepact request message.
         * @returns The telepact response message.
         */
        return await this.server.process(message);
    }

    private createFunctionRoutes(telepactSchema: TelepactSchema): FunctionRoutes {
        const functionRoutes = Object.fromEntries(
            Object.keys(telepactSchema.parsed)
                .filter(isAutoMockFunctionName)
                .map((functionName) => [
                    functionName,
                    async (_functionName: string, requestMessage: any): Promise<any> =>
                        await handleAutoMockFunction(
                            requestMessage,
                            this.stubs,
                            this.invocations,
                            this.random,
                            telepactSchema,
                            this.enableGeneratedDefaultStub,
                            this.enableOptionalFieldGeneration,
                            this.randomizeOptionalFieldGeneration,
                        ),
                ]),
        ) as FunctionRoutes;

        return {
            ...functionRoutes,
            'fn.createStub_': async (_functionName, requestMessage) => await handleCreateStub(requestMessage, this.stubs),
            'fn.verify_': async (_functionName, requestMessage) => await handleVerify(requestMessage, this.invocations),
            'fn.verifyNoMoreInteractions_': async () => await handleVerifyNoMoreInteractions(this.invocations),
            'fn.clearCalls_': async () => await handleClearCalls(this.invocations),
            'fn.clearStubs_': async () => await handleClearStubs(this.stubs),
            'fn.setRandomSeed_': async (_functionName, requestMessage) => await handleSetRandomSeed(requestMessage, this.random),
        };
    }
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

function isAutoMockFunctionName(typeName: string): boolean {
    return typeName.startsWith('fn.') && !typeName.endsWith('.->') && !typeName.endsWith('_');
}
