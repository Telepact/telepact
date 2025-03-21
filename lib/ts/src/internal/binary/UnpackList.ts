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

import { MsgpackPacked } from './PackList';
import { unpack } from './Unpack';
import { unpackMap } from './UnpackMap';

export function unpackList(list: any[]): any[] {
    if (list.length === 0) {
        return list;
    }

    if (!(list[0] instanceof MsgpackPacked)) {
        const newList: any[] = [];
        for (const e of list) {
            newList.push(unpack(e));
        }
        return newList;
    }

    const unpackedList: any[] = [];
    const headers: any[] = list[1];

    for (let i = 2; i < list.length; i += 1) {
        const row: any[] = list[i];
        const m = unpackMap(row, headers);

        unpackedList.push(m);
    }

    return unpackedList;
}
