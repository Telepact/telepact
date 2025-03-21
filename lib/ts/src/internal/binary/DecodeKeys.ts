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
import { BinaryEncodingMissing } from '../../internal/binary/BinaryEncodingMissing';

export function decodeKeys(given: any, binaryEncoder: BinaryEncoding): any {
    if (given instanceof Map) {
        const newMap: { [key: string]: any } = {};

        for (const [key, value] of given.entries()) {
            const finalKey = typeof key === 'string' ? key : binaryEncoder.decodeMap.get(key);

            if (finalKey === undefined) {
                throw new BinaryEncodingMissing(key);
            }

            const decodedValue = decodeKeys(value, binaryEncoder);
            newMap[finalKey] = decodedValue;
        }

        return newMap;
    } else if (Array.isArray(given)) {
        return given.map((value) => decodeKeys(value, binaryEncoder));
    } else {
        return given;
    }
}
