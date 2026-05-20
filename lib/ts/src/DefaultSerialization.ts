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

import { addExtension, Packr, Unpackr } from 'msgpackr';
import { BinaryEncoding } from './internal/binary/BinaryEncoding.js';
import { BinaryEncodedBody } from './internal/binary/BinaryEncodedBody.js';
import { Serialization } from './Serialization.js';

function encodeBinaryValue(value: any, binaryEncoder: BinaryEncoding): any {
    if (value === null || value === undefined) {
        return value;
    }

    if (Array.isArray(value)) {
        const result = new Array(value.length);
        for (let index = 0; index < value.length; index += 1) {
            result[index] = encodeBinaryValue(value[index], binaryEncoder);
        }
        return result;
    }

    if (value instanceof Map) {
        const newMap = new Map<any, any>();
        for (const [key, item] of value.entries()) {
            const mappedKey = typeof key === 'string' ? (binaryEncoder.encodeMap.get(key) ?? key) : key;
            newMap.set(mappedKey, encodeBinaryValue(item, binaryEncoder));
        }
        return newMap;
    }

    if (typeof value === 'object') {
        const newMap = new Map<any, any>();
        for (const key of Object.keys(value)) {
            const mappedKey = binaryEncoder.encodeMap.get(key) ?? key;
            newMap.set(mappedKey, encodeBinaryValue(value[key], binaryEncoder));
        }
        return newMap;
    }

    return value;
}

addExtension({
    Class: BinaryEncodedBody,
    write(instance: BinaryEncodedBody) {
        return encodeBinaryValue(instance.value, instance.binaryEncoder);
    },
});

export class DefaultSerialization implements Serialization {
    private textEncoder = new TextEncoder();
    private textDecoder = new TextDecoder();
    private packr = new Packr({ mapsAsObjects: false, useRecords: false });
    private unpackr = new Unpackr({ mapsAsObjects: false, useRecords: false });

    public toJson(telepactMessage: any): Uint8Array {
        const jsonStr = JSON.stringify(telepactMessage);
        return this.textEncoder.encode(jsonStr);
    }

    public toMsgpack(telepactMessage: any): Uint8Array {
        return this.packr.encode(telepactMessage);
    }

    public fromJson(bytes: Uint8Array): any {
        const jsonStr = this.textDecoder.decode(bytes);
        return JSON.parse(jsonStr);
    }

    public fromMsgpack(bytes: Uint8Array): any {
        return this.unpackr.decode(bytes);
    }
}
