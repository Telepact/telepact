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
import { BinaryPlan, BinaryStructPlan, BinaryTaggedPlan, BinaryUnionPlan } from '../../internal/binary/BinaryBodyPlan.js';
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

const scalarPlan: BinaryPlan = { kind: 'scalar' };

function createTaggedPlan(
    sourceKey: string,
    valuePlan: BinaryPlan,
    binaryEncoding: Map<string, number>,
): BinaryTaggedPlan {
    return {
        sourceKey,
        encodedKey: binaryEncoding.get(sourceKey) ?? sourceKey,
        valuePlan,
    };
}

function createStructPlan(fields: BinaryTaggedPlan[]): BinaryStructPlan {
    return {
        kind: 'struct',
        fields,
        fieldsBySourceKey: new Map(fields.map((field) => [field.sourceKey, field])),
        fieldsByEncodedKey: new Map(fields.map((field) => [field.encodedKey, field])),
    };
}

function createUnionPlan(tags: BinaryTaggedPlan[]): BinaryUnionPlan {
    return {
        kind: 'union',
        tags,
        tagsBySourceKey: new Map(tags.map((tag) => [tag.sourceKey, tag])),
        tagsByEncodedKey: new Map(tags.map((tag) => [tag.encodedKey, tag])),
    };
}

function buildTypePlan(typeDeclaration: TTypeDeclaration, binaryEncoding: Map<string, number>): BinaryPlan {
    if (typeDeclaration.type instanceof TArray) {
        return {
            kind: 'array',
            itemPlan: buildTypePlan(typeDeclaration.typeParameters[0], binaryEncoding),
        };
    }

    if (typeDeclaration.type instanceof TObject) {
        return {
            kind: 'object',
            valuePlan: buildTypePlan(typeDeclaration.typeParameters[0], binaryEncoding),
        };
    }

    if (typeDeclaration.type instanceof TStruct) {
        const fields = Object.entries(typeDeclaration.type.fields).map(([sourceKey, field]) =>
            createTaggedPlan(sourceKey, buildTypePlan(field.typeDeclaration, binaryEncoding), binaryEncoding),
        );
        return createStructPlan(fields);
    }

    if (typeDeclaration.type instanceof TUnion) {
        const tags = Object.entries(typeDeclaration.type.tags).map(([sourceKey, value]) =>
            createTaggedPlan(sourceKey, createStructPlan(Object.entries(value.fields).map(([fieldKey, field]) =>
                createTaggedPlan(fieldKey, buildTypePlan(field.typeDeclaration, binaryEncoding), binaryEncoding),
            )), binaryEncoding),
        );
        return createUnionPlan(tags);
    }

    return scalarPlan;
}

export function constructBinaryEncoding(telepactSchema: TelepactSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();

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

    const finalString = sortedAllKeys.join('\n');
    const checksum = createChecksum(finalString);

    const rootPlans: BinaryTaggedPlan[] = [];
    for (const [key, value] of Object.entries(telepactSchema.parsed)) {
        if (key.startsWith('fn.') && value instanceof TUnion && value.tags[key] !== undefined) {
            rootPlans.push(
                createTaggedPlan(
                    key,
                    createStructPlan(Object.entries(value.tags[key].fields).map(([fieldKey, field]) =>
                        createTaggedPlan(fieldKey, buildTypePlan(field.typeDeclaration, binaryEncoding), binaryEncoding),
                    )),
                    binaryEncoding,
                ),
            );
        }
    }

    return new BinaryEncoding(binaryEncoding, checksum, rootPlans);
}
