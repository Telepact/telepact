//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
