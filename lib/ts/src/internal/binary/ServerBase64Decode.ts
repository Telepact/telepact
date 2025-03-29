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

import { decodeBase64 } from "./Base64Util";

export function serverBase64Decode(body: Record<string, any>, bytesPaths: Record<string, any>): void {
    travelBase64Decode(body, bytesPaths);
}

function travelBase64Decode(value: any, bytesPaths: any): any {
    if (typeof bytesPaths === "object" && !Array.isArray(bytesPaths)) {
        for (const [key, val] of Object.entries(bytesPaths)) {
            if (val === true) {
                if (key === "*" && Array.isArray(value)) {
                    for (let i = 0; i < value.length; i++) {
                        const nv = travelBase64Decode(value[i], val);
                        value[i] = nv;
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const [k, v] of Object.entries(value)) {
                        const nv = travelBase64Decode(v, val);
                        value[k] = nv;
                    }
                } else if (typeof value === "object" && value !== null) {
                    const nv = travelBase64Decode(value[key], val);
                    value[key] = nv;
                } else {
                    throw new Error(`Invalid bytes path: ${key} for value: ${value}`);
                }
            } else {
                if (key === "*" && Array.isArray(value)) {
                    for (let i = 0; i < value.length; i++) {
                        travelBase64Decode(value[i], val);
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const [k, v] of Object.entries(value)) {
                        travelBase64Decode(v, val);
                    }
                } else if (typeof value === "object" && value !== null) {
                    travelBase64Decode(value[key], val);
                } else {
                    throw new Error(`Invalid bytes path: ${key} for value: ${value}`);
                }
            }
        }
        return null;
    } else if (bytesPaths === true && (typeof value === "string" || value === null)) {
        if (value === null) {
            return null;
        }
        const decodedValue = decodeBase64(value as string);
        return decodedValue;
    } else {
        throw new Error(`Invalid bytes path: ${bytesPaths} for value: ${value} of type ${typeof value}`);
    }
}