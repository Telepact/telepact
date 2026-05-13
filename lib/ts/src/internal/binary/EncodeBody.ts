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

import { BinaryEncoding } from '../../internal/binary/BinaryEncoding.js';
import { BinaryPlan, BinaryStructPlan, BinaryTaggedPlan, BinaryUnionPlan } from '../../internal/binary/BinaryBodyPlan.js';
import { encodeKeys } from '../../internal/binary/EncodeKeys.js';

function encodePlannedValue(value: any, plan: BinaryPlan, binaryEncoder: BinaryEncoding): any {
    if (value === null || value === undefined) {
        return value;
    }

    if (plan.kind === 'scalar') {
        return value;
    }

    if (plan.kind === 'array') {
        if (!Array.isArray(value)) {
            return encodeKeys(value, binaryEncoder);
        }
        const result = new Array(value.length);
        for (let index = 0; index < value.length; index += 1) {
            result[index] = encodePlannedValue(value[index], plan.itemPlan, binaryEncoder);
        }
        return result;
    }

    if (plan.kind === 'object') {
        if (typeof value !== 'object' || Array.isArray(value)) {
            return encodeKeys(value, binaryEncoder);
        }
        const result = new Map<any, any>();
        for (const key in value) {
            if (Object.prototype.hasOwnProperty.call(value, key)) {
                const finalKey = binaryEncoder.encodeMap.get(key) ?? key;
                result.set(finalKey, encodePlannedValue(value[key], plan.valuePlan, binaryEncoder));
            }
        }
        return result;
    }

    if (plan.kind === 'union') {
        return encodePlannedUnion(value, plan, binaryEncoder);
    }

    return encodePlannedStruct(value, plan, binaryEncoder);
}

function encodePlannedStruct(value: any, plan: BinaryStructPlan, binaryEncoder: BinaryEncoding): Map<any, any> | any {
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
        return encodeKeys(value, binaryEncoder);
    }

    const objectValue = value as Record<string, any>;
    const result = new Map<any, any>();
    let handledFieldCount = 0;
    for (const field of plan.fields) {
        if (Object.prototype.hasOwnProperty.call(objectValue, field.sourceKey)) {
            handledFieldCount += 1;
            result.set(field.encodedKey, encodePlannedValue(objectValue[field.sourceKey], field.valuePlan, binaryEncoder));
        }
    }

    const objectKeys = Object.keys(objectValue);
    if (handledFieldCount !== objectKeys.length) {
        for (const key of objectKeys) {
            if (!plan.fieldsBySourceKey.has(key)) {
                const finalKey = binaryEncoder.encodeMap.get(key) ?? key;
                result.set(finalKey, encodeKeys(objectValue[key], binaryEncoder));
            }
        }
    }

    return result;
}

function encodePlannedUnion(value: any, plan: BinaryUnionPlan, binaryEncoder: BinaryEncoding): Map<any, any> | any {
    if (typeof value !== 'object' || value === null || Array.isArray(value)) {
        return encodeKeys(value, binaryEncoder);
    }

    const objectKeys = Object.keys(value);
    if (objectKeys.length !== 1) {
        return encodeKeys(value, binaryEncoder);
    }

    const tag = plan.tagsBySourceKey.get(objectKeys[0]);
    if (tag === undefined) {
        return encodeKeys(value, binaryEncoder);
    }

    const result = new Map<any, any>();
    result.set(tag.encodedKey, encodePlannedValue(value[tag.sourceKey], tag.valuePlan, binaryEncoder));
    return result;
}

export function encodeBody(messageBody: Record<string, any>, binaryEncoder: BinaryEncoding): Map<any, any> {
    const rootKeys = Object.keys(messageBody);
    if (rootKeys.length === 1) {
        const rootPlan = binaryEncoder.rootPlansBySourceKey.get(rootKeys[0]);
        if (rootPlan !== undefined) {
            const result = new Map<any, any>();
            result.set(rootPlan.encodedKey, encodePlannedValue(messageBody[rootPlan.sourceKey], rootPlan.valuePlan, binaryEncoder));
            return result;
        }
    }

    return encodeKeys(messageBody, binaryEncoder);
}
