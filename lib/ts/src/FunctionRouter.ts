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

import { Message } from './Message.js';

export type ServerFunction = (headers: Record<string, any>, arguments_: Record<string, any>) => Promise<Message>;
export type ServerMiddleware = (requestMessage: Message, functionRouter: FunctionRouter) => Promise<Message>;

type RegisteredFunction = {
    authenticated: boolean;
    handler: ServerFunction;
};

export class FunctionRouter {
    private readonly functions: Map<string, RegisteredFunction>;

    constructor() {
        this.functions = new Map<string, RegisteredFunction>();
    }

    register(functionName: string, handler: ServerFunction): FunctionRouter {
        return this.registerUnauthenticated(functionName, handler);
    }

    registerUnauthenticated(functionName: string, handler: ServerFunction): FunctionRouter {
        this.functions.set(functionName, { authenticated: false, handler });
        return this;
    }

    registerAuthenticated(functionName: string, handler: ServerFunction): FunctionRouter {
        this.functions.set(functionName, { authenticated: true, handler });
        return this;
    }

    async route(requestMessage: Message): Promise<Message> {
        const functionName = requestMessage.getBodyTarget();
        const arguments_ = requestMessage.getBodyPayload();
        const registration = this.functions.get(functionName);
        if (registration === undefined) {
            throw new Error(`Unknown function: ${functionName}`);
        }
        if (registration.authenticated) {
            const authResult = requestMessage.headers['@result'];
            if (authResult !== undefined) {
                return new Message({}, authResult as Record<string, any>);
            }
            if (!('@auth_' in requestMessage.headers)) {
                return new Message({}, { ErrorUnauthenticated_: { 'message!': 'Valid authentication is required.' } });
            }
        }
        return await registration.handler(requestMessage.headers, arguments_);
    }
}
