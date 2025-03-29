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

import { encodeBase64 } from "./Base64Util";

export function serverBase64Encode(message: object[]): void {
    const headers = message[0] as Record<string, any>;
    const body = message[1] as Record<string, any>;

    const base64Paths = headers["@base64_"] as Record<string, any> || {};

    travelBase64Encode(body, base64Paths);
}

function travelBase64Encode(value: any, base64Paths: any): any {
    if (typeof base64Paths === "object" && !Array.isArray(base64Paths)) {
        for (const [key, val] of Object.entries(base64Paths)) {
            if (val === true) {
                if (key === "*" && Array.isArray(value)) {
                    for (let i = 0; i < value.length; i++) {
                        value[i] = travelBase64Encode(value[i], val);
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const k in value) {
                        value[k] = travelBase64Encode(value[k], val);
                    }
                } else if (typeof value === "object" && value !== null) {
                    value[key] = travelBase64Encode(value[key], val);
                } else {
                    throw new Error(`Invalid base64 path: ${key} for value: ${value}`);
                }
            } else {
                if (key === "*" && Array.isArray(value)) {
                    for (const v of value) {
                        travelBase64Encode(v, val);
                    }
                } else if (key === "*" && typeof value === "object" && value !== null) {
                    for (const v of Object.values(value)) {
                        travelBase64Encode(v, val);
                    }
                } else if (typeof value === "object" && value !== null) {
                    travelBase64Encode(value[key], val);
                } else {
                    throw new Error(`Invalid base64 path: ${key} for value: ${value}`);
                }
            }
        }
        return null;
    } else if (base64Paths === true && (Buffer.isBuffer(value) || value === null)) {
        if (value === null) {
            return null;
        }
        return encodeBase64(value);
    } else {
        throw new Error(`Invalid base64 path: ${base64Paths} for value: ${value}`);
    }
}