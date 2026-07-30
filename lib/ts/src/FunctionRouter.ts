//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { Message } from './Message.js';

export type FunctionRoute = (functionName: string, requestMessage: Message) => Promise<Message>;
export type FunctionRoutes = Record<string, FunctionRoute>;

export class FunctionRouter {
    functionRoutes: FunctionRoutes;

    constructor(functionRoutes: FunctionRoutes = {}) {
        this.functionRoutes = { ...functionRoutes };
    }

    async route(requestMessage: Message): Promise<Message> {
        const functionName = requestMessage.getBodyTarget();
        const functionRoute = this.functionRoutes[functionName];
        if (functionRoute === undefined) {
            throw new Error(`Unknown function: ${functionName}`);
        }

        return await functionRoute(functionName, requestMessage);
    }
}
