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

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding.js';

export function encodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (given === null || given === undefined) {
        return given;
    }

    if (Array.isArray(given)) {
        const result = new Array(given.length);
        for (let index = 0; index < given.length; index += 1) {
            result[index] = encodeKeys(given[index], binaryEncoder);
        }
        return result;
    }

    if (typeof given === 'object') {
        return createEncodedMapView(given as Record<string, any>, binaryEncoder);
    }

    return given;
}

function createEncodedMapView(given: Record<string, any>, binaryEncoder: BinaryEncoding): Map<any, any> {
    const view = {
        constructor: Map,
        get size() {
            return Object.keys(given).length;
        },
        *[Symbol.iterator](): IterableIterator<[any, any]> {
            for (const key in given) {
                if (Object.prototype.hasOwnProperty.call(given, key)) {
                    yield [binaryEncoder.encodeMap.get(key) ?? key, encodeKeys(given[key], binaryEncoder)];
                }
            }
        },
    };

    return view as unknown as Map<any, any>;
}
