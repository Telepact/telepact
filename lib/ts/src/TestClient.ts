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

import { Client } from "./Client";
import { Message } from "./Message";
import { isSubMap } from "./internal/mock/IsSubMap";
import { RandomGenerator } from './RandomGenerator';
import { TelepactSchema } from './TelepactSchema';
import { TUnion } from './internal/types/TUnion';
import { GenerateContext } from './internal/generation/GenerateContext';

export class TestClientOptions {
    generatedCollectionLengthMin: number;
    generatedCollectionLengthMax: number;

    constructor() {
        this.generatedCollectionLengthMin = 0;
        this.generatedCollectionLengthMax = 3;
    }
}

export class TestClient {
    private client: Client;
    private random: RandomGenerator;
    private schema: TelepactSchema | null = null;

    constructor(client: Client, options: TestClientOptions) {
        this.client = client;
        this.random = new RandomGenerator(options.generatedCollectionLengthMin, options.generatedCollectionLengthMax);
    }

    async assertRequest(
        requestMessage: Message,
        expectedPseudoJsonBody: Record<string, unknown>,
        expectMatch: boolean,
    ): Promise<Message> {
        if (this.schema == null) {
            const response = await this.client.request(new Message({}, { 'fn.api_': {} }));
            const api = (response.body['Ok_'] as Record<string, unknown>)['api'] as any[];
            this.schema = TelepactSchema.fromJson(JSON.stringify(api));
        }

        const responseMessage = await this.client.request(requestMessage);

        const didMatch = isSubMap(expectedPseudoJsonBody, responseMessage.body);

        if (expectMatch) {
            if (!didMatch) {
                throw new Error(
                    `Expected response body was not a sub map. Expected: ${JSON.stringify(
                        expectedPseudoJsonBody,
                    )} Actual: ${JSON.stringify(responseMessage.body)}`,
                );
            } else {
                return responseMessage;
            }
        } else {
            if (didMatch) {
                throw new Error(
                    `Expected response body was a sub map. Expected: ${JSON.stringify(
                        expectedPseudoJsonBody,
                    )} Actual: ${JSON.stringify(responseMessage.body)}`,
                );
            } else {
                const useBlueprintValue = true;
                const includeOptionalFields = false;
                const alwaysIncludeRequiredFields = true;
                const randomizeOptionalFieldGeneration = false;

                const functionName = requestMessage.getBodyTarget();
                const definition = this.schema.parsed[`${functionName}.->`] as TUnion;

                const generatedResult = definition.generateRandomValue(
                    expectedPseudoJsonBody,
                    useBlueprintValue,
                    [],
                    new GenerateContext(
                        includeOptionalFields,
                        randomizeOptionalFieldGeneration,
                        alwaysIncludeRequiredFields,
                        functionName,
                        this.random,
                    ),
                );

                return new Message(responseMessage.headers, generatedResult);
            }
        }
    }

    setSeed(seed: number) {
        this.random.setSeed(seed);
    }
}