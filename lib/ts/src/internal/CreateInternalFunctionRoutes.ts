//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { FunctionRoutes } from '../FunctionRouter.js';
import { Message } from '../Message.js';
import { TelepactSchema } from '../TelepactSchema.js';
import { getApiDefinitionsWithExamples } from './GetApiDefinitionsWithExamples.js';

export function createInternalFunctionRoutes(telepactSchema: TelepactSchema): FunctionRoutes {
    return {
        'fn.ping_': async (): Promise<Message> => new Message({}, { Ok_: {} }),
        'fn.api_': async (_functionName: string, requestMessage: Message): Promise<Message> => {
            const requestPayload = requestMessage.getBodyPayload();
            const includeInternal = requestPayload['includeInternal!'] === true;
            const includeExamples = requestPayload['includeExamples!'] === true;
            const apiDefinitions = includeExamples
                ? getApiDefinitionsWithExamples(telepactSchema, includeInternal)
                : includeInternal
                    ? telepactSchema.full
                    : telepactSchema.original;
            return new Message({}, { Ok_: { api: apiDefinitions } });
        },
    };
}
