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

import { TelepactSchema } from '../../TelepactSchema.js';
import { BinaryEncoding } from '../../internal/binary/BinaryEncoding.js';
import { createChecksum } from '../../internal/binary/CreateChecksum.js';
import { TUnion } from '../types/TUnion.js';
import { TStruct } from '../types/TStruct.js';
import { TArray } from '../types/TArray.js';
import { TObject } from '../types/TObject.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';

function traceType(typeDeclaration: TTypeDeclaration): string[] {
    const thisAllKeys: string[] = [];

    if (typeDeclaration.type instanceof TArray) {
        const theseKeys2 = traceType(typeDeclaration.typeParameters[0]);
        thisAllKeys.push(...theseKeys2);
    } else if (typeDeclaration.type instanceof TObject) {
        const theseKeys2 = traceType(typeDeclaration.typeParameters[0]);
        thisAllKeys.push(...theseKeys2);
    } else if (typeDeclaration.type instanceof TStruct) {
        const structFields = typeDeclaration.type.fields;
        for (const [structFieldKey, structField] of Object.entries(structFields)) {
            thisAllKeys.push(structFieldKey);
            const moreKeys = traceType(structField.typeDeclaration);
            thisAllKeys.push(...moreKeys);
        }
    } else if (typeDeclaration.type instanceof TUnion) {
        const unionTags = typeDeclaration.type.tags;
        for (const [tagKey, tagValue] of Object.entries(unionTags)) {
            thisAllKeys.push(tagKey);
            const structFields = tagValue.fields;
            for (const [structFieldKey, structField] of Object.entries(structFields)) {
                thisAllKeys.push(structFieldKey);
                const moreKeys = traceType(structField.typeDeclaration);
                thisAllKeys.push(...moreKeys);
            }
        }
    }

    return thisAllKeys;
}

function compileTypeDescriptor(typeDeclaration: TTypeDeclaration, encodeMap: Map<string, number>, visitedTypeNames: Set<string> = new Set()): any {
    if (typeDeclaration.type instanceof TArray) {
        return {
            t: 'a',
            i: compileTypeDescriptor(typeDeclaration.typeParameters[0], encodeMap, visitedTypeNames),
        };
    }

    if (typeDeclaration.type instanceof TObject) {
        return { t: 'd' };
    }

    if (typeDeclaration.type instanceof TStruct) {
        if (visitedTypeNames.has(typeDeclaration.type.name)) {
            return { t: 'd' };
        }
        const nextVisited = new Set(visitedTypeNames);
        nextVisited.add(typeDeclaration.type.name);
        return {
            t: 's',
            f: Object.entries(typeDeclaration.type.fields).map(([fieldKey, field]) => [
                encodeMap.get(fieldKey),
                compileTypeDescriptor(field.typeDeclaration, encodeMap, nextVisited),
            ]),
        };
    }

    if (typeDeclaration.type instanceof TUnion) {
        if (visitedTypeNames.has(typeDeclaration.type.name)) {
            return { t: 'd' };
        }
        const nextVisited = new Set(visitedTypeNames);
        nextVisited.add(typeDeclaration.type.name);
        return {
            t: 'u',
            g: Object.entries(typeDeclaration.type.tags).map(([tagKey, tagValue]) => [
                encodeMap.get(tagKey),
                {
                    t: 's',
                    f: Object.entries(tagValue.fields).map(([fieldKey, field]) => [
                        encodeMap.get(fieldKey),
                        compileTypeDescriptor(field.typeDeclaration, encodeMap, nextVisited),
                    ]),
                },
            ]),
        };
    }

    return { t: 'v' };
}

export function constructBinaryEncoding(telepactSchema: TelepactSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();
    const requestPlanDescriptors: any[][] = [];
    const responsePlanDescriptors: any[][] = [];

    for (const [key, value] of Object.entries(telepactSchema.parsed)) {

        if (key.endsWith('.->') && value instanceof TUnion) {
            const result = value.tags['Ok_'];
            allKeys.add('Ok_');
            Object.entries(result.fields).forEach(([fieldKey, field]) => {
                allKeys.add(fieldKey);
                const keys = traceType(field.typeDeclaration);
                keys.forEach((key) => allKeys.add(key));
            });
    
        } else if (key.startsWith('fn.') && value instanceof TUnion) {
            allKeys.add(key);
            const args = value.tags[key];
            Object.entries(args.fields).forEach(([fieldKey, field]) => {
                allKeys.add(fieldKey);
                const keys = traceType(field.typeDeclaration);
                keys.forEach((key) => allKeys.add(key));
            });
        }
    }

    const sortedAllKeys = Array.from(allKeys).sort();

    const binaryEncoding = new Map<string, number>();
    sortedAllKeys.forEach((key, index) => {
        binaryEncoding.set(key, index);
    });

    for (const [key, value] of Object.entries(telepactSchema.parsed)) {
        if (!(key.startsWith('fn.')) || !(value instanceof TUnion) || !(`${key}.->` in telepactSchema.parsed)) {
            continue;
        }
        requestPlanDescriptors.push([
            binaryEncoding.get(key),
            {
                t: 's',
                f: Object.entries(value.tags[key].fields).map(([fieldKey, field]) => [
                    binaryEncoding.get(fieldKey),
                    compileTypeDescriptor(field.typeDeclaration, binaryEncoding),
                ]),
            },
        ]);

        const responseType = telepactSchema.parsed[`${key}.->`] as TUnion;
        responsePlanDescriptors.push([
            binaryEncoding.get(key),
            {
                t: 's',
                f: Object.entries(responseType.tags['Ok_'].fields).map(([fieldKey, field]) => [
                    binaryEncoding.get(fieldKey),
                    compileTypeDescriptor(field.typeDeclaration, binaryEncoding),
                ]),
            },
        ]);
    }

    const finalString = sortedAllKeys.join('\n');
    const checksum = createChecksum(finalString);

    return new BinaryEncoding(binaryEncoding, checksum, sortedAllKeys, requestPlanDescriptors, responsePlanDescriptors);
}
