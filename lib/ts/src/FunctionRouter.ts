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
export type ServerNext = (
    headers: Record<string, any>,
    functionName: string,
    arguments_: Record<string, any>,
) => Promise<Message>;
export type ServerMiddleware = (
    headers: Record<string, any>,
    functionName: string,
    arguments_: Record<string, any>,
    next: ServerNext,
) => Promise<Message>;

export class FunctionRouter {
    private readonly functions: Map<string, ServerFunction>;

    constructor() {
        this.functions = new Map<string, ServerFunction>();
    }

    register(functionName: string, handler: ServerFunction): FunctionRouter {
        this.functions.set(functionName, handler);
        return this;
    }

    async middleware(
        headers: Record<string, any>,
        functionName: string,
        arguments_: Record<string, any>,
        next: ServerNext,
    ): Promise<Message> {
        const handler = this.functions.get(functionName);
        if (handler !== undefined) {
            return await handler(headers, arguments_);
        }
        return await next(headers, functionName, arguments_);
    }
}
