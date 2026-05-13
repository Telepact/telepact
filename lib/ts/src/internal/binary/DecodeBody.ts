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
import { BinaryPlan, BinaryStructPlan, BinaryUnionPlan } from '../../internal/binary/BinaryBodyPlan.js';
import { BinaryEncodingMissing } from '../../internal/binary/BinaryEncodingMissing.js';
import { decodeKeys } from '../../internal/binary/DecodeKeys.js';

function decodePlannedValue(value: any, plan: BinaryPlan, binaryEncoder: BinaryEncoding): any {
    if (value === null || value === undefined) {
        return value;
    }

    if (plan.kind === 'scalar') {
        return value;
    }

    if (plan.kind === 'array') {
        if (!Array.isArray(value)) {
            return decodeKeys(value, binaryEncoder);
        }
        const result = new Array(value.length);
        for (let index = 0; index < value.length; index += 1) {
            result[index] = decodePlannedValue(value[index], plan.itemPlan, binaryEncoder);
        }
        return result;
    }

    if (plan.kind === 'object') {
        if (!(value instanceof Map)) {
            return decodeKeys(value, binaryEncoder);
        }
        const result: Record<string, any> = {};
        for (const [key, item] of value.entries()) {
            const finalKey = typeof key === 'string' ? key : binaryEncoder.decodeMap.get(key);
            if (finalKey === undefined) {
                throw new BinaryEncodingMissing(key);
            }
            result[finalKey] = decodePlannedValue(item, plan.valuePlan, binaryEncoder);
        }
        return result;
    }

    if (plan.kind === 'union') {
        return decodePlannedUnion(value, plan, binaryEncoder);
    }

    return decodePlannedStruct(value, plan, binaryEncoder);
}

function decodePlannedStruct(value: any, plan: BinaryStructPlan, binaryEncoder: BinaryEncoding): any {
    if (!(value instanceof Map)) {
        return decodeKeys(value, binaryEncoder);
    }

    const result: Record<string, any> = {};
    for (const [key, item] of value.entries()) {
        const plannedField = plan.fieldsByEncodedKey.get(key)
            ?? (typeof key === 'string' ? plan.fieldsBySourceKey.get(key) : undefined);
        if (plannedField !== undefined) {
            result[plannedField.sourceKey] = decodePlannedValue(item, plannedField.valuePlan, binaryEncoder);
            continue;
        }

        if (typeof key === 'string') {
            result[key] = decodeKeys(item, binaryEncoder);
            continue;
        }

        const finalKey = binaryEncoder.decodeMap.get(key);
        if (finalKey === undefined) {
            throw new BinaryEncodingMissing(key);
        }
        result[finalKey] = decodeKeys(item, binaryEncoder);
    }
    return result;
}

function decodePlannedUnion(value: any, plan: BinaryUnionPlan, binaryEncoder: BinaryEncoding): any {
    if (!(value instanceof Map) || value.size !== 1) {
        return decodeKeys(value, binaryEncoder);
    }

    const [key, item] = value.entries().next().value as [string | number, any];
    const plannedTag = plan.tagsByEncodedKey.get(key)
        ?? (typeof key === 'string' ? plan.tagsBySourceKey.get(key) : undefined);
    if (plannedTag === undefined) {
        return decodeKeys(value, binaryEncoder);
    }

    return {
        [plannedTag.sourceKey]: decodePlannedValue(item, plannedTag.valuePlan, binaryEncoder),
    };
}

export function decodeBody(encodedMessageBody: Map<any, any>, binaryEncoder: BinaryEncoding): Record<string, any> {
    if (encodedMessageBody.size === 1) {
        const [key, value] = encodedMessageBody.entries().next().value as [string | number, any];
        const rootPlan = binaryEncoder.rootPlansByEncodedKey.get(key)
            ?? (typeof key === 'string' ? binaryEncoder.rootPlansBySourceKey.get(key) : undefined);
        if (rootPlan !== undefined) {
            return {
                [rootPlan.sourceKey]: decodePlannedValue(value, rootPlan.valuePlan, binaryEncoder),
            };
        }
    }

    return decodeKeys(encodedMessageBody, binaryEncoder);
}
