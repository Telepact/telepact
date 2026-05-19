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

import { MsgpackPacked } from './PackList.js';
import { unpack } from './Unpack.js';
import { unpackMap } from './UnpackMap.js';
import { measureSerializerStage } from '../../SerializerMeasurement.js';

export function unpackList(list: any[]): any[] {
    return measureSerializerStage('deserialize.binary.unpackList', () => {
        if (list.length === 0) {
            return list;
        }

        if (!(list[0] instanceof MsgpackPacked)) {
            const newList = new Array(list.length);
            for (let index = 0; index < list.length; index += 1) {
                newList[index] = unpack(list[index]);
            }
            return newList;
        }

        const unpackedList = new Array(list.length - 2);
        const headers: any[] = list[1];

        for (let i = 2; i < list.length; i += 1) {
            const row: any[] = list[i];
            unpackedList[i - 2] = unpackMap(row, headers);
        }

        return unpackedList;
    });
}
