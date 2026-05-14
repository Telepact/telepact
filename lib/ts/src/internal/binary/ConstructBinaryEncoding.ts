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
import { BinaryEncoding, BinaryPackHeader, BinaryPackSiteData } from '../../internal/binary/BinaryEncoding.js';
import { createChecksum } from '../../internal/binary/CreateChecksum.js';
import { TUnion } from '../types/TUnion.js';
import { TStruct } from '../types/TStruct.js';
import { TArray } from '../types/TArray.js';
import { TObject } from '../types/TObject.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';
import { TFieldDeclaration } from '../types/TFieldDeclaration.js';

function traceType(typeDeclaration: TTypeDeclaration, visitedTypeNames: Set<string> = new Set()): string[] {
    const thisAllKeys: string[] = [];

    if (typeDeclaration.type instanceof TArray) {
        const childType = typeDeclaration.typeParameters[0];
        if (childType !== undefined) {
            thisAllKeys.push(...traceType(childType, visitedTypeNames));
        }
    } else if (typeDeclaration.type instanceof TObject) {
        const childType = typeDeclaration.typeParameters[0];
        if (childType !== undefined) {
            thisAllKeys.push(...traceType(childType, visitedTypeNames));
        }
    } else if (typeDeclaration.type instanceof TStruct) {
        if (visitedTypeNames.has(typeDeclaration.type.name)) {
            return thisAllKeys;
        }
        visitedTypeNames.add(typeDeclaration.type.name);
        const structFields = typeDeclaration.type.fields;
        for (const [structFieldKey, structField] of Object.entries(structFields)) {
            thisAllKeys.push(structFieldKey);
            thisAllKeys.push(...traceType(structField.typeDeclaration, visitedTypeNames));
        }
    } else if (typeDeclaration.type instanceof TUnion) {
        if (visitedTypeNames.has(typeDeclaration.type.name)) {
            return thisAllKeys;
        }
        visitedTypeNames.add(typeDeclaration.type.name);
        const unionTags = typeDeclaration.type.tags;
        for (const [tagKey, tagValue] of Object.entries(unionTags)) {
            thisAllKeys.push(tagKey);
            for (const [structFieldKey, structField] of Object.entries(tagValue.fields)) {
                thisAllKeys.push(structFieldKey);
                thisAllKeys.push(...traceType(structField.typeDeclaration, visitedTypeNames));
            }
        }
    }

    return thisAllKeys;
}

function isDeterministicPackedStruct(typeDeclaration: TTypeDeclaration, visitingTypeNames: Set<string>): boolean {
    if (typeDeclaration.type instanceof TArray) {
        const childType = typeDeclaration.typeParameters[0];
        if (childType === undefined) {
            return true;
        }
        return !(childType.type instanceof TStruct || childType.type instanceof TUnion);
    }

    if (typeDeclaration.type instanceof TObject) {
        return true;
    }

    if (typeDeclaration.type instanceof TStruct) {
        if (visitingTypeNames.has(typeDeclaration.type.name)) {
            return false;
        }
        const nextVisitingTypeNames = new Set(visitingTypeNames);
        nextVisitingTypeNames.add(typeDeclaration.type.name);
        return Object.values(typeDeclaration.type.fields)
            .every((field) => isDeterministicPackedStruct(field.typeDeclaration, nextVisitingTypeNames));
    }

    if (typeDeclaration.type instanceof TUnion) {
        if (visitingTypeNames.has(typeDeclaration.type.name)) {
            return false;
        }
        const nextVisitingTypeNames = new Set(visitingTypeNames);
        nextVisitingTypeNames.add(typeDeclaration.type.name);
        return Object.values(typeDeclaration.type.tags)
            .every((tagValue) => Object.values(tagValue.fields)
                .every((field) => isDeterministicPackedStruct(field.typeDeclaration, nextVisitingTypeNames)));
    }

    return true;
}

function getEncodedKey(binaryEncoding: Map<string, number>, key: string): number {
    const encodedKey = binaryEncoding.get(key);
    if (encodedKey === undefined) {
        throw new Error(`Missing binary encoding for key ${key}`);
    }
    return encodedKey;
}

function buildNestedHeader(key: string, typeDeclaration: TTypeDeclaration, binaryEncoding: Map<string, number>): number | BinaryPackHeader {
    const encodedKey = getEncodedKey(binaryEncoding, key);

    if (typeDeclaration.type instanceof TStruct) {
        const header: BinaryPackHeader = [encodedKey];
        for (const [fieldKey, field] of Object.entries(typeDeclaration.type.fields)) {
            header.push(buildNestedHeader(fieldKey, field.typeDeclaration, binaryEncoding));
        }
        return header;
    }

    if (typeDeclaration.type instanceof TUnion) {
        const header: BinaryPackHeader = [encodedKey];
        for (const [tagKey, tagValue] of Object.entries(typeDeclaration.type.tags)) {
            const tagHeader: BinaryPackHeader = [getEncodedKey(binaryEncoding, tagKey)];
            for (const [fieldKey, field] of Object.entries(tagValue.fields)) {
                tagHeader.push(buildNestedHeader(fieldKey, field.typeDeclaration, binaryEncoding));
            }
            header.push(tagHeader);
        }
        return header;
    }

    return encodedKey;
}

function buildPackHeader(structType: TStruct, binaryEncoding: Map<string, number>): BinaryPackHeader {
    const header: BinaryPackHeader = [null];
    for (const [fieldKey, field] of Object.entries(structType.fields)) {
        header.push(buildNestedHeader(fieldKey, field.typeDeclaration, binaryEncoding));
    }
    return header;
}

function collectPackedSites(
    path: string[],
    typeDeclaration: TTypeDeclaration,
    binaryEncoding: Map<string, number>,
    packedSites: BinaryPackSiteData[],
    visitedTypeNames: Set<string> = new Set(),
): void {
    if (typeDeclaration.type instanceof TArray) {
        const childType = typeDeclaration.typeParameters[0];
        if (childType !== undefined
            && childType.type instanceof TStruct
            && isDeterministicPackedStruct(childType, new Set())) {
            packedSites.push([[...path], buildPackHeader(childType.type, binaryEncoding)]);
        }
        return;
    }

    if (typeDeclaration.type instanceof TObject) {
        return;
    }

    if (typeDeclaration.type instanceof TStruct) {
        if (visitedTypeNames.has(typeDeclaration.type.name)) {
            return;
        }
        const nextVisitedTypeNames = new Set(visitedTypeNames);
        nextVisitedTypeNames.add(typeDeclaration.type.name);
        for (const [fieldKey, field] of Object.entries(typeDeclaration.type.fields)) {
            collectPackedSites([...path, fieldKey], field.typeDeclaration, binaryEncoding, packedSites, nextVisitedTypeNames);
        }
        return;
    }

    if (typeDeclaration.type instanceof TUnion) {
        if (visitedTypeNames.has(typeDeclaration.type.name)) {
            return;
        }
        const nextVisitedTypeNames = new Set(visitedTypeNames);
        nextVisitedTypeNames.add(typeDeclaration.type.name);
        for (const [tagKey, tagValue] of Object.entries(typeDeclaration.type.tags)) {
            for (const [fieldKey, field] of Object.entries(tagValue.fields)) {
                collectPackedSites([...path, tagKey, fieldKey], field.typeDeclaration, binaryEncoding, packedSites, nextVisitedTypeNames);
            }
        }
    }
}

function addRootPackedSites(rootPath: string[], fields: { [key: string]: TFieldDeclaration }, binaryEncoding: Map<string, number>, packedSites: BinaryPackSiteData[]): void {
    for (const [fieldKey, field] of Object.entries(fields)) {
        collectPackedSites([...rootPath, fieldKey], field.typeDeclaration, binaryEncoding, packedSites);
    }
}

export function constructBinaryEncoding(telepactSchema: TelepactSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();

    for (const [key, value] of Object.entries(telepactSchema.parsed)) {
        if (key.endsWith('.->') && value instanceof TUnion) {
            const result = value.tags['Ok_'];
            if (result !== undefined) {
                allKeys.add('Ok_');
                Object.entries(result.fields).forEach(([fieldKey, field]) => {
                    allKeys.add(fieldKey);
                    traceType(field.typeDeclaration).forEach((nestedKey) => allKeys.add(nestedKey));
                });
            }
        } else if (key.startsWith('fn.') && value instanceof TUnion) {
            allKeys.add(key);
            const args = value.tags[key];
            if (args !== undefined) {
                Object.entries(args.fields).forEach(([fieldKey, field]) => {
                    allKeys.add(fieldKey);
                    traceType(field.typeDeclaration).forEach((nestedKey) => allKeys.add(nestedKey));
                });
            }
        }
    }

    const sortedAllKeys = Array.from(allKeys).sort();

    const binaryEncoding = new Map<string, number>();
    sortedAllKeys.forEach((key, index) => {
        binaryEncoding.set(key, index);
    });

    const packedSites: BinaryPackSiteData[] = [];
    for (const [key, value] of Object.entries(telepactSchema.parsed)) {
        if (key.endsWith('.->') && value instanceof TUnion) {
            const result = value.tags['Ok_'];
            if (result !== undefined) {
                addRootPackedSites(['Ok_'], result.fields, binaryEncoding, packedSites);
            }
        } else if (key.startsWith('fn.') && value instanceof TUnion) {
            const args = value.tags[key];
            if (args !== undefined) {
                addRootPackedSites([key], args.fields, binaryEncoding, packedSites);
            }
        }
    }

    const finalString = sortedAllKeys.join('\n');
    const checksum = createChecksum(finalString);

    return new BinaryEncoding(binaryEncoding, checksum, packedSites);
}
