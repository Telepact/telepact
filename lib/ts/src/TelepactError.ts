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

export type TelepactErrorKind = 'parse' | 'validation' | 'serialization' | 'transport' | 'handler';

function fillRandomValues(bytes: Uint8Array): void {
    const cryptoObject = globalThis.crypto;
    if (typeof cryptoObject?.getRandomValues === 'function') {
        cryptoObject.getRandomValues(bytes);
        return;
    }

    for (let i = 0; i < bytes.length; i += 1) {
        bytes[i] = Math.floor(Math.random() * 256);
    }
}

function createCaseId(): string {
    const cryptoObject = globalThis.crypto;
    if (typeof cryptoObject?.randomUUID === 'function') {
        return cryptoObject.randomUUID();
    }

    const bytes = new Uint8Array(16);
    fillRandomValues(bytes);
    bytes[6] = (bytes[6] & 0x0f) | 0x40;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    const hex = Array.from(bytes, (byte) => byte.toString(16).padStart(2, '0')).join('');
    return `${hex.slice(0, 8)}-${hex.slice(8, 12)}-${hex.slice(12, 16)}-${hex.slice(16, 20)}-${hex.slice(20)}`;
}

function toError(error: unknown): Error | undefined {
    if (error instanceof Error) {
        return error;
    }
    if (typeof error === 'string') {
        return new Error(error);
    }
    if (error === undefined || error === null) {
        return undefined;
    }
    return new Error(String(error));
}

export class TelepactError extends Error {
    kind?: TelepactErrorKind;
    caseId: string;
    override cause?: Error;

    constructor(message: string, kind?: TelepactErrorKind, cause?: unknown);
    constructor(cause: unknown, kind?: TelepactErrorKind);
    constructor(arg: string | unknown, kind?: TelepactErrorKind, cause?: unknown) {
        const resolvedCause = typeof arg === 'string' ? toError(cause) : toError(arg);
        const message = typeof arg === 'string'
            ? arg
            : resolvedCause?.message ?? 'telepact error';

        super(message);
        Object.setPrototypeOf(this, TelepactError.prototype);

        this.name = 'TelepactError';
        this.kind = kind;
        this.caseId = createCaseId();
        this.cause = resolvedCause;

        if (resolvedCause?.stack) {
            this.stack = resolvedCause.stack;
        }
    }
}
