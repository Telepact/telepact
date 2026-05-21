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
import { TAny } from '../types/TAny.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';

function traceType(typeDeclaration: TTypeDeclaration): string[] {
    const thisAllKeys: string[] = [];

    if (typeDeclaration.type instanceof TArray) {
        const theseKeys2 = traceType(typeDeclaration.typeParameters[0]);
        thisAllKeys.push(...theseKeys2);
    } else if (typeDeclaration.type instanceof TAny) {
        return thisAllKeys;
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

function buildPackHeader(typeDeclaration: TTypeDeclaration, rootKey: string | null = null): any[] {
    const header: any[] = [rootKey];
    if (!(typeDeclaration.type instanceof TStruct)) {
        return header;
    }
    for (const [fieldKey, field] of Object.entries(typeDeclaration.type.fields)) {
        if (field.typeDeclaration.type instanceof TStruct) {
            header.push(buildPackHeader(field.typeDeclaration, fieldKey));
        } else {
            header.push(fieldKey);
        }
    }
    return header;
}

function collectPackSites(
    typeDeclaration: TTypeDeclaration,
    path: string[],
    packSites: any[][],
    activeTypeNames: Set<string> = new Set(),
    underGenericList = false,
): void {
    if (typeDeclaration.type instanceof TArray) {
        const itemType = typeDeclaration.typeParameters[0];
        if (!underGenericList && itemType.type instanceof TStruct) {
            packSites.push([[...path], buildPackHeader(itemType)]);
            return;
        }
        collectPackSites(itemType, path, packSites, activeTypeNames, true);
        return;
    }
    if (typeDeclaration.type instanceof TAny || typeDeclaration.type instanceof TObject) {
        return;
    }
    if (typeDeclaration.type instanceof TStruct) {
        if (activeTypeNames.has(typeDeclaration.type.name)) {
            return;
        }
        const nextActive = new Set(activeTypeNames);
        nextActive.add(typeDeclaration.type.name);
        for (const [fieldKey, field] of Object.entries(typeDeclaration.type.fields)) {
            collectPackSites(field.typeDeclaration, [...path, fieldKey], packSites, nextActive, underGenericList);
        }
        return;
    }
    if (typeDeclaration.type instanceof TUnion) {
        if (activeTypeNames.has(typeDeclaration.type.name)) {
            return;
        }
        const nextActive = new Set(activeTypeNames);
        nextActive.add(typeDeclaration.type.name);
        for (const [tagKey, tagValue] of Object.entries(typeDeclaration.type.tags)) {
            for (const [fieldKey, field] of Object.entries(tagValue.fields)) {
                collectPackSites(field.typeDeclaration, [...path, tagKey, fieldKey], packSites, nextActive, underGenericList);
            }
        }
    }
}

export function constructBinaryEncoding(telepactSchema: TelepactSchema): BinaryEncoding {
    const allKeys: Set<string> = new Set();
    const packSites: any[][] = [];

    for (const [key, value] of Object.entries(telepactSchema.parsed)) {

        if (key.endsWith('.->') && value instanceof TUnion) {
            const result = value.tags['Ok_'];
            allKeys.add('Ok_');
            Object.entries(result.fields).forEach(([fieldKey, field]) => {
                allKeys.add(fieldKey);
                const keys = traceType(field.typeDeclaration);
                keys.forEach((key) => allKeys.add(key));
                collectPackSites(field.typeDeclaration, ['Ok_', fieldKey], packSites);
            });
    
        } else if (key.startsWith('fn.') && value instanceof TUnion) {
            allKeys.add(key);
            const args = value.tags[key];
            Object.entries(args.fields).forEach(([fieldKey, field]) => {
                allKeys.add(fieldKey);
                const keys = traceType(field.typeDeclaration);
                keys.forEach((key) => allKeys.add(key));
                collectPackSites(field.typeDeclaration, [key, fieldKey], packSites);
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

    return new BinaryEncoding(binaryEncoding, checksum, packSites as any);
}
