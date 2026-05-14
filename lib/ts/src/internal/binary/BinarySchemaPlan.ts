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

import { BinaryEncodingMissing } from './BinaryEncodingMissing.js';
import { pack } from './Pack.js';
import { MSGPACK_PACKED_VALUE } from './PackList.js';
import { MSGPACK_UNDEFINED_VALUE } from './PackMap.js';
import { TelepactSchema } from '../../TelepactSchema.js';
import { TArray } from '../types/TArray.js';
import { TObject } from '../types/TObject.js';
import { TStruct } from '../types/TStruct.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';
import { TUnion } from '../types/TUnion.js';

const hasOwn = Object.prototype.hasOwnProperty;

export const RESPONSE_FUNCTION_NAME = Symbol('telepactResponseFunctionName');
export type BinaryResponseHeaders = Record<string, any> & { [RESPONSE_FUNCTION_NAME]?: string };

type EncodeValue = (value: unknown) => unknown;
type DecodeValue = (value: unknown) => unknown;

interface PackedStructPlan {
    readonly header: unknown[];
    encodeRow(value: Record<string, unknown>): unknown[];
}

interface ValuePlan {
    encode(value: unknown): unknown;
    encodePacked(value: unknown): unknown;
    decode(value: unknown): unknown;
    readonly encodesMap: boolean;
    readonly packedStruct: PackedStructPlan | undefined;
}

interface RootPlan {
    encode(value: Record<string, unknown>): Map<unknown, unknown>;
    encodePacked(value: Record<string, unknown>): Map<unknown, unknown>;
    decode(value: Map<unknown, unknown>): Record<string, unknown>;
}

interface StructFieldPlan {
    readonly key: string;
    readonly encodedKey: number;
    readonly typeDeclaration: TTypeDeclaration;
    readonly valuePlan: ValuePlan;
}

function isRecord(value: unknown): value is Record<string, unknown> {
    return typeof value === 'object' && value !== null && !Array.isArray(value) && !(value instanceof Map);
}

function encodeGeneric(value: unknown, encodeMap: Map<string, number>): unknown {
    if (value === null || value === undefined) {
        return value;
    }

    if (Array.isArray(value)) {
        const result = new Array(value.length);
        for (let index = 0; index < value.length; index += 1) {
            result[index] = encodeGeneric(value[index], encodeMap);
        }
        return result;
    }

    if (value instanceof Map) {
        const result = new Map<unknown, unknown>();
        for (const [key, nested] of value.entries()) {
            result.set(key, encodeGeneric(nested, encodeMap));
        }
        return result;
    }

    if (isRecord(value)) {
        const result = new Map<unknown, unknown>();
        for (const key in value) {
            if (hasOwn.call(value, key)) {
                const encodedKey = encodeMap.get(key) ?? key;
                result.set(encodedKey, encodeGeneric(value[key], encodeMap));
            }
        }
        return result;
    }

    return value;
}

function encodePackedGeneric(value: unknown, encodeMap: Map<string, number>): unknown {
    return pack(encodeGeneric(value, encodeMap));
}

function decodeGeneric(value: unknown, decodeMap: Map<number, string>): unknown {
    if (Array.isArray(value)) {
        const result = new Array(value.length);
        for (let index = 0; index < value.length; index += 1) {
            result[index] = decodeGeneric(value[index], decodeMap);
        }
        return result;
    }

    if (value instanceof Map) {
        const result: Record<string, unknown> = {};
        for (const [key, nested] of value.entries()) {
            const decodedKey = typeof key === 'string' ? key : decodeMap.get(key);
            if (decodedKey === undefined) {
                throw new BinaryEncodingMissing(key);
            }
            result[decodedKey] = decodeGeneric(nested, decodeMap);
        }
        return result;
    }

    return value;
}

function getOnlyEntryFromMap(value: Map<unknown, unknown>): [unknown, unknown] | undefined {
    for (const entry of value.entries()) {
        return entry;
    }
    return undefined;
}

function compileValuePlan(
    typeDeclaration: TTypeDeclaration,
    encodeMap: Map<string, number>,
    decodeMap: Map<number, string>,
): ValuePlan {
    const nullable = typeDeclaration.nullable;
    const type = typeDeclaration.type;

    let encodeCore: EncodeValue;
    let encodePackedCore: EncodeValue;
    let decodeCore: DecodeValue;
    let encodesMap = false;
    let packedStruct: PackedStructPlan | undefined;

    if (type instanceof TArray) {
        const itemPlan = compileValuePlan(typeDeclaration.typeParameters[0]!, encodeMap, decodeMap);
        encodeCore = (value: unknown): unknown => {
            if (!Array.isArray(value)) {
                return encodeGeneric(value, encodeMap);
            }

            const result = new Array(value.length);
            for (let index = 0; index < value.length; index += 1) {
                result[index] = itemPlan.encode(value[index]);
            }
            return result;
        };
        encodePackedCore = (value: unknown): unknown => {
            if (!Array.isArray(value)) {
                return encodePackedGeneric(value, encodeMap);
            }

            if (itemPlan.packedStruct !== undefined) {
                try {
                    return encodePackedStructArray(value, itemPlan.packedStruct);
                } catch (error) {
                    if (!(error instanceof CannotDirectPackError)) {
                        throw error;
                    }
                }
            }

            const encodedList = new Array(value.length);
            for (let index = 0; index < value.length; index += 1) {
                encodedList[index] = itemPlan.encode(value[index]);
            }
            return pack(encodedList);
        };
        decodeCore = (value: unknown): unknown => {
            if (!Array.isArray(value)) {
                return decodeGeneric(value, decodeMap);
            }

            const result = new Array(value.length);
            for (let index = 0; index < value.length; index += 1) {
                result[index] = itemPlan.decode(value[index]);
            }
            return result;
        };
    } else if (type instanceof TObject) {
        const itemPlan = compileValuePlan(typeDeclaration.typeParameters[0]!, encodeMap, decodeMap);
        encodesMap = true;
        encodeCore = (value: unknown): unknown => {
            if (!isRecord(value)) {
                return encodeGeneric(value, encodeMap);
            }

            const result = new Map<unknown, unknown>();
            for (const key in value) {
                if (hasOwn.call(value, key)) {
                    const encodedKey = encodeMap.get(key) ?? key;
                    result.set(encodedKey, itemPlan.encode(value[key]));
                }
            }
            return result;
        };
        encodePackedCore = (value: unknown): unknown => {
            if (!isRecord(value)) {
                return encodePackedGeneric(value, encodeMap);
            }

            const result = new Map<unknown, unknown>();
            for (const key in value) {
                if (hasOwn.call(value, key)) {
                    const encodedKey = encodeMap.get(key) ?? key;
                    result.set(encodedKey, itemPlan.encodePacked(value[key]));
                }
            }
            return result;
        };
        decodeCore = (value: unknown): unknown => {
            if (!(value instanceof Map)) {
                return decodeGeneric(value, decodeMap);
            }

            const result: Record<string, unknown> = {};
            for (const [key, nested] of value.entries()) {
                const decodedKey = typeof key === 'string' ? key : decodeMap.get(key);
                if (decodedKey === undefined) {
                    throw new BinaryEncodingMissing(key);
                }
                result[decodedKey] = itemPlan.decode(nested);
            }
            return result;
        };
    } else if (type instanceof TStruct) {
        const fieldPlans = Object.entries(type.fields)
            .map(([key, field]) => {
                const encodedKey = encodeMap.get(key);
                if (encodedKey === undefined) {
                    throw new Error(`Missing binary encoding for field ${key}`);
                }
                return {
                    key,
                    encodedKey,
                    typeDeclaration: field.typeDeclaration,
                    valuePlan: compileValuePlan(field.typeDeclaration, encodeMap, decodeMap),
                } satisfies StructFieldPlan;
            });
        const knownFieldNames = new Set(fieldPlans.map((fieldPlan) => fieldPlan.key));
        encodesMap = true;
        encodeCore = (value: unknown): unknown => {
            if (!isRecord(value)) {
                return encodeGeneric(value, encodeMap);
            }

            const result = new Map<unknown, unknown>();
            for (const fieldPlan of fieldPlans) {
                if (hasOwn.call(value, fieldPlan.key)) {
                    result.set(fieldPlan.encodedKey, fieldPlan.valuePlan.encode(value[fieldPlan.key]));
                }
            }
            return result;
        };
        encodePackedCore = (value: unknown): unknown => {
            if (!isRecord(value)) {
                return encodePackedGeneric(value, encodeMap);
            }

            const result = new Map<unknown, unknown>();
            for (const fieldPlan of fieldPlans) {
                if (hasOwn.call(value, fieldPlan.key)) {
                    result.set(fieldPlan.encodedKey, fieldPlan.valuePlan.encodePacked(value[fieldPlan.key]));
                }
            }
            return result;
        };
        decodeCore = (value: unknown): unknown => {
            if (!(value instanceof Map)) {
                return decodeGeneric(value, decodeMap);
            }

            const result: Record<string, unknown> = {};
            for (const fieldPlan of fieldPlans) {
                if (value.has(fieldPlan.encodedKey)) {
                    result[fieldPlan.key] = fieldPlan.valuePlan.decode(value.get(fieldPlan.encodedKey));
                }
            }
            for (const [key, nested] of value.entries()) {
                const decodedKey = typeof key === 'string' ? key : decodeMap.get(key);
                if (decodedKey === undefined) {
                    throw new BinaryEncodingMissing(key);
                }
                if (!knownFieldNames.has(decodedKey)) {
                    result[decodedKey] = decodeGeneric(nested, decodeMap);
                }
            }
            return result;
        };
        packedStruct = buildPackedStructPlan(fieldPlans);
    } else if (type instanceof TUnion) {
        const tagPlans = Object.entries(type.tags).flatMap(([tagName, tagStruct]) => {
            const encodedKey = encodeMap.get(tagName);
            if (encodedKey === undefined) {
                return [];
            }
            const tagPlan = compileValuePlan(new TTypeDeclaration(tagStruct, false, []), encodeMap, decodeMap);
            return [{
                tagName,
                encodedKey,
                tagPlan,
            }];
        });
        const tagByDecodedKey = new Map<string, typeof tagPlans[number]>();
        const tagByEncodedKey = new Map<number, typeof tagPlans[number]>();
        for (const tagPlan of tagPlans) {
            tagByDecodedKey.set(tagPlan.tagName, tagPlan);
            tagByEncodedKey.set(tagPlan.encodedKey, tagPlan);
        }
        encodesMap = true;
        encodeCore = (value: unknown): unknown => {
            if (!isRecord(value)) {
                return encodeGeneric(value, encodeMap);
            }

            for (const tagPlan of tagPlans) {
                if (hasOwn.call(value, tagPlan.tagName)) {
                    const result = new Map<unknown, unknown>();
                    result.set(tagPlan.encodedKey, tagPlan.tagPlan.encode(value[tagPlan.tagName]));
                    return result;
                }
            }

            return encodeGeneric(value, encodeMap);
        };
        encodePackedCore = (value: unknown): unknown => {
            if (!isRecord(value)) {
                return encodePackedGeneric(value, encodeMap);
            }

            for (const tagPlan of tagPlans) {
                if (hasOwn.call(value, tagPlan.tagName)) {
                    const result = new Map<unknown, unknown>();
                    result.set(tagPlan.encodedKey, tagPlan.tagPlan.encodePacked(value[tagPlan.tagName]));
                    return result;
                }
            }

            return encodePackedGeneric(value, encodeMap);
        };
        decodeCore = (value: unknown): unknown => {
            if (!(value instanceof Map)) {
                return decodeGeneric(value, decodeMap);
            }

            if (value.size !== 1) {
                return decodeGeneric(value, decodeMap);
            }

            const entry = getOnlyEntryFromMap(value);
            if (entry === undefined) {
                return {};
            }

            const [encodedTag, payload] = entry;
            const tagPlan = typeof encodedTag === 'string'
                ? tagByDecodedKey.get(encodedTag)
                : typeof encodedTag === 'number'
                    ? tagByEncodedKey.get(encodedTag)
                    : undefined;
            if (tagPlan === undefined) {
                return decodeGeneric(value, decodeMap);
            }

            return { [tagPlan.tagName]: tagPlan.tagPlan.decode(payload) };
        };
    } else {
        encodeCore = (value: unknown): unknown => value;
        encodePackedCore = (value: unknown): unknown => value;
        decodeCore = (value: unknown): unknown => value;
    }

    return {
        encode(value: unknown): unknown {
            if (nullable && (value === null || value === undefined)) {
                return value;
            }
            return encodeCore(value);
        },
        encodePacked(value: unknown): unknown {
            if (nullable && (value === null || value === undefined)) {
                return value;
            }
            return encodePackedCore(value);
        },
        decode(value: unknown): unknown {
            if (nullable && (value === null || value === undefined)) {
                return value;
            }
            return decodeCore(value);
        },
        encodesMap,
        packedStruct,
    };
}

function buildPackedStructPlan(fieldPlans: StructFieldPlan[]): PackedStructPlan | undefined {
    const header: unknown[] = [null];
    const packedFieldPlans = fieldPlans.map((fieldPlan, index) => {
        const nestedPackedStruct = fieldPlan.valuePlan.packedStruct;
        const nullable = fieldPlan.typeDeclaration.nullable;

        if (fieldPlan.valuePlan.encodesMap) {
            if (nestedPackedStruct === undefined || nullable) {
                return undefined;
            }
            header.push([fieldPlan.encodedKey, ...nestedPackedStruct.header.slice(1)]);
        } else {
            header.push(fieldPlan.encodedKey);
        }

        return {
            fieldPlan,
            index,
            nestedPackedStruct,
        };
    });

    if (packedFieldPlans.some((fieldPlan) => fieldPlan === undefined)) {
        return undefined;
    }

    const resolvedPackedFieldPlans = packedFieldPlans as Array<{
        fieldPlan: StructFieldPlan;
        index: number;
        nestedPackedStruct: PackedStructPlan | undefined;
    }>;

    return {
        header,
        encodeRow(value: Record<string, unknown>): unknown[] {
            if (!isRecord(value)) {
                throw new CannotDirectPackError();
            }

            const row: unknown[] = [];
            for (const packedFieldPlan of resolvedPackedFieldPlans) {
                const fieldName = packedFieldPlan.fieldPlan.key;
                if (!hasOwn.call(value, fieldName)) {
                    continue;
                }

                const rawValue = value[fieldName];
                let encodedValue: unknown;
                if (packedFieldPlan.nestedPackedStruct !== undefined) {
                    if (!isRecord(rawValue)) {
                        throw new CannotDirectPackError();
                    }
                    encodedValue = packedFieldPlan.nestedPackedStruct.encodeRow(rawValue);
                } else {
                    encodedValue = packedFieldPlan.fieldPlan.valuePlan.encodePacked(rawValue);
                }

                while (row.length < packedFieldPlan.index) {
                    row.push(MSGPACK_UNDEFINED_VALUE);
                }

                if (row.length === packedFieldPlan.index) {
                    row.push(encodedValue);
                } else {
                    row[packedFieldPlan.index] = encodedValue;
                }
            }
            return row;
        },
    };
}

function encodePackedStructArray(list: unknown[], packedStructPlan: PackedStructPlan): unknown[] {
    if (list.length === 0) {
        return list;
    }

    const packedList: unknown[] = [MSGPACK_PACKED_VALUE, packedStructPlan.header];
    for (const item of list) {
        if (!isRecord(item)) {
            throw new CannotDirectPackError();
        }
        packedList.push(packedStructPlan.encodeRow(item));
    }
    return packedList;
}

function compileRootPlan(
    unionType: TUnion,
    encodeMap: Map<string, number>,
    decodeMap: Map<number, string>,
): RootPlan {
    const valuePlan = compileValuePlan(new TTypeDeclaration(unionType, false, []), encodeMap, decodeMap);
    return {
        encode(value: Record<string, unknown>): Map<unknown, unknown> {
            return valuePlan.encode(value) as Map<unknown, unknown>;
        },
        encodePacked(value: Record<string, unknown>): Map<unknown, unknown> {
            return valuePlan.encodePacked(value) as Map<unknown, unknown>;
        },
        decode(value: Map<unknown, unknown>): Record<string, unknown> {
            return valuePlan.decode(value) as Record<string, unknown>;
        },
    };
}

export class BinarySchemaPlan {
    private readonly requestPlansByName: Map<string, RootPlan>;
    private readonly requestPlansByEncodedKey: Map<number, RootPlan>;
    private readonly responsePlansByFunction: Map<string, RootPlan>;

    private constructor(
        requestPlansByName: Map<string, RootPlan>,
        requestPlansByEncodedKey: Map<number, RootPlan>,
        responsePlansByFunction: Map<string, RootPlan>,
    ) {
        this.requestPlansByName = requestPlansByName;
        this.requestPlansByEncodedKey = requestPlansByEncodedKey;
        this.responsePlansByFunction = responsePlansByFunction;
    }

    static compile(
        telepactSchema: TelepactSchema,
        encodeMap: Map<string, number>,
        decodeMap: Map<number, string>,
    ): BinarySchemaPlan {
        const requestPlansByName = new Map<string, RootPlan>();
        const requestPlansByEncodedKey = new Map<number, RootPlan>();
        const responsePlansByFunction = new Map<string, RootPlan>();

        for (const [schemaKey, parsedType] of Object.entries(telepactSchema.parsed)) {
            if (schemaKey.startsWith('fn.') && !schemaKey.endsWith('.->') && parsedType instanceof TUnion) {
                const plan = compileRootPlan(parsedType, encodeMap, decodeMap);
                requestPlansByName.set(schemaKey, plan);
                const encodedKey = encodeMap.get(schemaKey);
                if (encodedKey !== undefined) {
                    requestPlansByEncodedKey.set(encodedKey, plan);
                }
            }

            if (schemaKey.endsWith('.->') && parsedType instanceof TUnion) {
                const functionName = schemaKey.slice(0, -3);
                responsePlansByFunction.set(functionName, compileRootPlan(parsedType, encodeMap, decodeMap));
            }
        }

        return new BinarySchemaPlan(requestPlansByName, requestPlansByEncodedKey, responsePlansByFunction);
    }

    decodeRequestBody(messageBody: Map<unknown, unknown>): Record<string, unknown> | undefined {
        const entry = getOnlyEntryFromMap(messageBody);
        if (entry === undefined) {
            return undefined;
        }

        const [target] = entry;
        const plan = typeof target === 'string'
            ? this.requestPlansByName.get(target)
            : typeof target === 'number'
                ? this.requestPlansByEncodedKey.get(target)
                : undefined;
        if (plan === undefined) {
            return undefined;
        }

        return plan.decode(messageBody);
    }

    encodeResponseBody(functionName: string, messageBody: Record<string, unknown>, packed: boolean): Map<unknown, unknown> | undefined {
        const plan = this.responsePlansByFunction.get(functionName);
        if (plan === undefined) {
            return undefined;
        }

        return packed ? plan.encodePacked(messageBody) : plan.encode(messageBody);
    }
}

class CannotDirectPackError extends Error {}
