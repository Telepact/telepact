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

export function convertMapsToObjects(value: any): any {
    if (value instanceof Map) {
        const newObj: Record<string, any> = {};
        for (const [key, val] of value.entries()) {
            newObj[key] = convertMapsToObjects(val);
        }
        return newObj;
    } else if (Array.isArray(value)) {
        const newList: any[] = [];
        for (const val of value) {
            const newVal = convertMapsToObjects(val);
            newList.push(newVal);
        }
        return newList;
    } else if (typeof value == 'object' && value !== null) {
        const newObj: Record<string, any> = {};
        for (const [key, val] of Object.entries(value)) {
            newObj[key] = convertMapsToObjects(val);
        }
    } else {
        return value;
    }
}
