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

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding';

export function encodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (given === null || given === undefined) {
        return given;
    } else if (typeof given === 'object' && !Array.isArray(given)) {
        const newMap = new Map<any, any>();

        for (const [key, value] of Object.entries(given)) {
            const finalKey = binaryEncoder.encodeMap.has(key) ? binaryEncoder.encodeMap.get(key) : key;
            const encodedValue = encodeKeys(value, binaryEncoder);

            newMap.set(finalKey, encodedValue);
        }

        return newMap;
    } else if (Array.isArray(given)) {
        return given.map((value) => encodeKeys(value, binaryEncoder));
    } else {
        return given;
    }
}
