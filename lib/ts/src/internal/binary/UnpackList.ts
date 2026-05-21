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

import { BinaryPackHeader } from './BinaryEncoding.js';
import { MsgpackPacked } from './PackList.js';
import { MsgpackUndefined } from './PackMap.js';

function unpackRow(row: any[], header: BinaryPackHeader): Map<any, any> {
    const finalMap = new Map<any, any>();

    for (let index = 0; index < row.length; index += 1) {
        const headerEntry = header[index + 1];
        const value = row[index];

        if (headerEntry === undefined || value instanceof MsgpackUndefined) {
            continue;
        }

        if (Array.isArray(headerEntry)) {
            if (Array.isArray(value)) {
                finalMap.set(headerEntry[0], unpackRow(value, headerEntry));
            }
        } else {
            finalMap.set(headerEntry, value);
        }
    }

    return finalMap;
}

export function unpackList(list: any[], header?: BinaryPackHeader): any[] {
    if (list.length === 0 || header === undefined || !(list[0] instanceof MsgpackPacked)) {
        return list;
    }

    const unpackedList = new Array(list.length - 1);
    for (let index = 1; index < list.length; index += 1) {
        const row = list[index];
        unpackedList[index - 1] = Array.isArray(row) ? unpackRow(row, header) : row;
    }

    return unpackedList;
}
