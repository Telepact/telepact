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

export type FunctionRoute = (functionName: string, requestMessage: Message) => Promise<Message>;
export type FunctionRoutes = Record<string, FunctionRoute>;

export class FunctionRouter {
    authenticatedFunctionRoutes: FunctionRoutes;
    unauthenticatedFunctionRoutes: FunctionRoutes;

    constructor() {
        this.authenticatedFunctionRoutes = {};
        this.unauthenticatedFunctionRoutes = {};
    }

    registerAuthenticatedRoutes(functionRoutes: FunctionRoutes): void {
        for (const [functionName, functionRoute] of Object.entries(functionRoutes)) {
            this.authenticatedFunctionRoutes[functionName] = functionRoute;
            delete this.unauthenticatedFunctionRoutes[functionName];
        }
    }

    registerUnauthenticatedRoutes(functionRoutes: FunctionRoutes): void {
        for (const [functionName, functionRoute] of Object.entries(functionRoutes)) {
            this.unauthenticatedFunctionRoutes[functionName] = functionRoute;
            delete this.authenticatedFunctionRoutes[functionName];
        }
    }

    hasAuthenticatedRoutes(): boolean {
        return Object.keys(this.authenticatedFunctionRoutes).length > 0;
    }

    requiresAuthentication(functionName: string): boolean {
        return functionName in this.authenticatedFunctionRoutes;
    }

    async route(requestMessage: Message): Promise<Message> {
        const functionName = requestMessage.getBodyTarget();
        const functionRoute = this.authenticatedFunctionRoutes[functionName]
            ?? this.unauthenticatedFunctionRoutes[functionName];
        if (functionRoute === undefined) {
            throw new Error(`Unknown function: ${functionName}`);
        }

        return await functionRoute(functionName, requestMessage);
    }
}
