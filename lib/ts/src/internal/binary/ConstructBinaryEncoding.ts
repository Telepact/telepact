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
import { BinaryEncoding, BinaryPackHeaderValue, BinaryPackSiteHeader } from '../../internal/binary/BinaryEncoding.js';
import { createChecksum } from '../../internal/binary/CreateChecksum.js';
import { TUnion } from '../types/TUnion.js';
import { TStruct } from '../types/TStruct.js';
import { TArray } from '../types/TArray.js';
import { TObject } from '../types/TObject.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';

function getSortedEntries<T>(record: Record<string, T>): Array<[string, T]> {
    return Object.entries(record).sort(([left], [right]) => left.localeCompare(right));
}

function traceType(typeDeclaration: TTypeDeclaration, visitedTypeNames: Set<string> = new Set()): string[] {
    const thisAllKeys: string[] = [];

    if (typeDeclaration.type instanceof TArray) {
        thisAllKeys.push(...traceType(typeDeclaration.typeParameters[0], visitedTypeNames));
    } else if (typeDeclaration.type instanceof TObject) {
        thisAllKeys.push(...traceType(typeDeclaration.typeParameters[0], visitedTypeNames));
    } else if (typeDeclaration.type instanceof TStruct) {
        const structType = typeDeclaration.type;
        if (visitedTypeNames.has(structType.name)) {
            return thisAllKeys;
        }
        const nextVisited = new Set(visitedTypeNames);
        nextVisited.add(structType.name);
        for (const [structFieldKey, structField] of getSortedEntries(structType.fields)) {
            thisAllKeys.push(structFieldKey);
            thisAllKeys.push(...traceType(structField.typeDeclaration, nextVisited));
        }
    } else if (typeDeclaration.type instanceof TUnion) {
        const unionType = typeDeclaration.type;
        if (visitedTypeNames.has(unionType.name)) {
            return thisAllKeys;
        }
        const nextVisited = new Set(visitedTypeNames);
        nextVisited.add(unionType.name);
        for (const [tagKey, tagValue] of getSortedEntries(unionType.tags)) {
            thisAllKeys.push(tagKey);
            for (const [structFieldKey, structField] of getSortedEntries(tagValue.fields)) {
                thisAllKeys.push(structFieldKey);
                thisAllKeys.push(...traceType(structField.typeDeclaration, nextVisited));
            }
        }
    }

    return thisAllKeys;
}

function buildNestedStructHeader(typeDeclaration: TTypeDeclaration, visitedTypeNames: Set<string> = new Set()): BinaryPackHeaderValue[] | null {
    if (!(typeDeclaration.type instanceof TStruct)) {
        return null;
    }

    const structType = typeDeclaration.type;
    if (visitedTypeNames.has(structType.name)) {
        return null;
    }

    const nextVisited = new Set(visitedTypeNames);
    nextVisited.add(structType.name);

    const nestedHeader: BinaryPackHeaderValue[] = [];
    for (const [fieldKey, field] of getSortedEntries(structType.fields)) {
        const childHeader = buildNestedStructHeader(field.typeDeclaration, nextVisited);
        if (childHeader === null) {
            nestedHeader.push(fieldKey);
        } else {
            nestedHeader.push([fieldKey, ...childHeader]);
        }
    }
    return nestedHeader;
}

function buildPackHeader(structType: TStruct): BinaryPackHeaderValue[] {
    const header: BinaryPackHeaderValue[] = [null];
    for (const [fieldKey, field] of getSortedEntries(structType.fields)) {
        const nestedHeader = buildNestedStructHeader(field.typeDeclaration, new Set([structType.name]));
        if (nestedHeader === null) {
            header.push(fieldKey);
        } else {
            header.push([fieldKey, ...nestedHeader]);
        }
    }
    return header;
}

function collectPackSites(
    typeDeclaration: TTypeDeclaration,
    path: string[],
    packSites: BinaryPackSiteHeader[],
    visitedTypeNames: Set<string> = new Set(),
): void {
    if (typeDeclaration.type instanceof TObject) {
        return;
    }

    if (typeDeclaration.type instanceof TArray) {
        const itemType = typeDeclaration.typeParameters[0];
        if (itemType.type instanceof TStruct) {
            packSites.push([path.slice(), buildPackHeader(itemType.type)]);
        }
        return;
    }

    if (typeDeclaration.type instanceof TStruct) {
        const structType = typeDeclaration.type;
        if (visitedTypeNames.has(structType.name)) {
            return;
        }
        const nextVisited = new Set(visitedTypeNames);
        nextVisited.add(structType.name);
        for (const [fieldKey, field] of getSortedEntries(structType.fields)) {
            collectPackSites(field.typeDeclaration, [...path, fieldKey], packSites, nextVisited);
        }
        return;
    }

    if (typeDeclaration.type instanceof TUnion) {
        const unionType = typeDeclaration.type;
        if (visitedTypeNames.has(unionType.name)) {
            return;
        }
        const nextVisited = new Set(visitedTypeNames);
        nextVisited.add(unionType.name);
        for (const [tagKey, tagValue] of getSortedEntries(unionType.tags)) {
            for (const [fieldKey, field] of getSortedEntries(tagValue.fields)) {
                collectPackSites(field.typeDeclaration, [...path, tagKey, fieldKey], packSites, nextVisited);
            }
        }
    }
}

function stringifyPackHeaderValue(value: BinaryPackHeaderValue): string {
    if (Array.isArray(value)) {
        return `[${value.map((item) => stringifyPackHeaderValue(item)).join(',')}]`;
    }
    if (value === null) {
        return 'null';
    }
    return String(value);
}

export function constructBinaryEncoding(telepactSchema: TelepactSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();
    const packSites: BinaryPackSiteHeader[] = [];

    for (const [key, value] of Object.entries(telepactSchema.parsed)) {
        if (key.endsWith('.->') && value instanceof TUnion) {
            const result = value.tags['Ok_'];
            allKeys.add('Ok_');
            for (const [fieldKey, field] of getSortedEntries(result.fields)) {
                allKeys.add(fieldKey);
                traceType(field.typeDeclaration).forEach((nestedKey) => allKeys.add(nestedKey));
                collectPackSites(field.typeDeclaration, ['Ok_', fieldKey], packSites);
            }
        } else if (key.startsWith('fn.') && value instanceof TUnion) {
            allKeys.add(key);
            const args = value.tags[key];
            for (const [fieldKey, field] of getSortedEntries(args.fields)) {
                allKeys.add(fieldKey);
                traceType(field.typeDeclaration).forEach((nestedKey) => allKeys.add(nestedKey));
                collectPackSites(field.typeDeclaration, [key, fieldKey], packSites);
            }
        }
    }

    const sortedAllKeys = Array.from(allKeys).sort();
    packSites.sort(([leftPath], [rightPath]) => leftPath.join('.').localeCompare(rightPath.join('.')));

    const binaryEncoding = new Map<string, number>();
    sortedAllKeys.forEach((key, index) => {
        binaryEncoding.set(key, index);
    });

    let finalString = sortedAllKeys.join('\n');
    if (packSites.length > 0) {
        finalString += `\n--encp--\n${packSites.map(([path, header]) => `${path.join('.')}:${stringifyPackHeaderValue(header)}`).join('\n')}`;
    }
    const checksum = createChecksum(finalString);

    return new BinaryEncoding(binaryEncoding, checksum, packSites);
}
