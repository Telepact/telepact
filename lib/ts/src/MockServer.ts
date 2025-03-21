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

import { TelepactSchema } from './TelepactSchema';
import { MockInvocation } from './internal/mock/MockInvocation';
import { MockStub } from './internal/mock/MockStub';
import { Server, ServerOptions as ServerOptions } from './Server';
import { RandomGenerator } from './RandomGenerator';
import { mockHandle } from './internal/mock/MockHandle';
import { MockTelepactSchema } from './MockTelepactSchema';

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

        this.server = new Server(telepactSchema, this.handle, serverOptions);
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
         * Process a given telepact Request Message into a telepact Response Message.
         *
         * @param message - The telepact request message.
         * @returns The telepact response message.
         */
        return await this.server.process(message);
    }

    private handle = async (requestMessage: any): Promise<any> => {
        return await mockHandle(
            requestMessage,
            this.stubs,
            this.invocations,
            this.random,
            this.server.telepactSchema,
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
