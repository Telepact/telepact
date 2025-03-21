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

export function getType(value: any): string {
    if (value === null) {
        return 'Null';
    } else if (typeof value === 'boolean') {
        return 'Boolean';
    } else if (typeof value === 'number') {
        return 'Number';
    } else if (typeof value === 'string') {
        return 'String';
    } else if (Array.isArray(value)) {
        return 'Array';
    } else if (typeof value === 'object') {
        return 'Object';
    } else {
        return 'Unknown';
    }
}
