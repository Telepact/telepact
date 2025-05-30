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

import { packList } from '../../internal/binary/PackList';

export function pack(value: any): any {
    if (Array.isArray(value)) {
        return packList(value);
    } else if (value instanceof Map) {
        const newMap: Map<any, any> = new Map();

        for (const [key, val] of value.entries()) {
            newMap.set(key, pack(val));
        }

        return newMap;
    } else {
        return value;
    }
}
