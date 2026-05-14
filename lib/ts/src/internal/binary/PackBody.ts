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

import { BinaryEncoding } from './BinaryEncoding.js';
import { packList } from './PackList.js';

function getParentMap(root: Map<any, any>, path: number[]): Map<any, any> | undefined {
    let current: any = root;
    for (let index = 0; index < path.length - 1; index += 1) {
        if (!(current instanceof Map)) {
            return undefined;
        }
        current = current.get(path[index]);
    }
    return current instanceof Map ? current : undefined;
}

export function packBody(body: Map<any, any>, binaryEncoding: BinaryEncoding): Map<any, any> {
    const result: Map<any, any> = new Map(body);

    for (const packedSite of binaryEncoding.packedSites) {
        const parentMap = getParentMap(result, packedSite.encodedPath);
        const targetKey = packedSite.encodedPath[packedSite.encodedPath.length - 1];
        if (parentMap === undefined || targetKey === undefined || !parentMap.has(targetKey)) {
            continue;
        }

        const value = parentMap.get(targetKey);
        if (Array.isArray(value)) {
            parentMap.set(targetKey, packList(value, packedSite.header));
        }
    }

    return result;
}
