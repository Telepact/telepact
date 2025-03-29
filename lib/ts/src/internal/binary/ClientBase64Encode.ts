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

export function clientBase64Encode(message: Array<any>): void {
    const body = message[1] as Record<string, any>;

    travelBase64Encode(body);
}

function travelBase64Encode(value: any): void {
    if (typeof value === "object" && !Array.isArray(value)) {
        for (const [key, val] of Object.entries(value)) {
            if (val instanceof Uint8Array) {
                value[key] = btoa(String.fromCharCode(...val));
            } else {
                travelBase64Encode(val);
            }
        }
    } else if (Array.isArray(value)) {
        for (let i = 0; i < value.length; i++) {
            const v = value[i];
            if (v instanceof Uint8Array) {
                value[i] = btoa(String.fromCharCode(...v));
            } else {
                travelBase64Encode(v);
            }
        }
    }
}