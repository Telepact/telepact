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

export function objectsAreEqual(obj1: any, obj2: any): boolean {
    // Check if both objects are the same type
    if (typeof obj1 !== typeof obj2) {
        return false;
    }

    // If objects are primitive types, compare directly
    if (typeof obj1 !== 'object' || obj1 === null || obj2 === null) {
        return obj1 === obj2;
    }

    // Check if both objects have the same keys
    const keys1 = Object.keys(obj1);
    const keys2 = Object.keys(obj2);
    if (keys1.length !== keys2.length || !keys1.every((key) => keys2.includes(key))) {
        return false;
    }

    // Recursively compare nested objects and arrays
    for (const key of keys1) {
        if (!objectsAreEqual(obj1[key], obj2[key])) {
            return false;
        }
    }

    // If all checks pass, objects are considered equal
    return true;
}
