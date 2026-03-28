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

import { MsgpackUndefined } from './PackMap';
import { unpack } from './Unpack';

export function unpackMap(row: any[], header: any[]): Map<any, any> {
    const finalMap = new Map<any, any>();

    for (let j = 0; j < row.length; j += 1) {
        const key = header[j + 1];
        const value = row[j];

        if (value instanceof MsgpackUndefined) {
            continue;
        }

        if (Array.isArray(key)) {
            const nestedHeader = key as any[];
            const nestedRow = value as any[];
            const m = unpackMap(nestedRow, nestedHeader);
            const i = nestedHeader[0] as number;
            finalMap.set(i, m);
        } else {
            const unpackedValue = unpack(value);
            finalMap.set(key, unpackedValue);
        }
    }

    return finalMap;
}
