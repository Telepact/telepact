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

function toError(error: unknown): Error {
    if (error instanceof Error) {
        return error;
    }
    if (typeof error === 'string') {
        return new Error(error);
    }
    return new Error(String(error));
}

export class SerializationError extends Error {
    context?: string;
    override cause?: Error;

    constructor(cause: unknown, context = 'serialize Telepact message') {
        const resolvedCause = toError(cause);
        super(`telepact serialization failed while ${context}: ${resolvedCause.message}`);
        Object.setPrototypeOf(this, SerializationError.prototype);

        this.name = 'SerializationError';
        this.context = context;
        this.cause = resolvedCause;

        if (resolvedCause.stack) {
            this.stack = resolvedCause.stack;
        }
    }
}
