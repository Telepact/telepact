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

import type { Serialization } from '../../Serialization.js';
import type { BinaryEncoding } from './BinaryEncoding.js';

export type MsgpackHeaders = {
    headers: Record<string, any>;
    bodyOffset: number;
};

export interface BinaryMsgpackSerialization extends Serialization {
    toBinaryMsgpack(headers: Record<string, any>, body: Record<string, any>, binaryEncoding: BinaryEncoding): Uint8Array;

    fromMsgpackHeaders(bytes: Uint8Array): MsgpackHeaders;

    fromMsgpackBody(bytes: Uint8Array, offset: number, binaryEncoding: BinaryEncoding): Record<string, any>;
}

export function isBinaryMsgpackSerialization(serializer: Serialization): serializer is BinaryMsgpackSerialization {
    const candidate = serializer as Partial<BinaryMsgpackSerialization>;
    return typeof candidate.toBinaryMsgpack === 'function'
        && typeof candidate.fromMsgpackHeaders === 'function'
        && typeof candidate.fromMsgpackBody === 'function';
}
