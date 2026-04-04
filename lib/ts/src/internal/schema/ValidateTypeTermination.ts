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

import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { SchemaParseFailure } from './SchemaParseFailure.js';
import { TArray } from '../types/TArray.js';
import { TFieldDeclaration } from '../types/TFieldDeclaration.js';
import { TObject } from '../types/TObject.js';
import { TStruct } from '../types/TStruct.js';
import { TType } from '../types/TType.js';
import { TTypeDeclaration } from '../types/TTypeDeclaration.js';
import { TUnion } from '../types/TUnion.js';

function typeDeclarationTerminates(
    typeDeclaration: TTypeDeclaration,
    terminatingTypeNames: Set<string>,
): boolean {
    if (typeDeclaration.nullable) {
        return true;
    }

    if (typeDeclaration.type instanceof TArray || typeDeclaration.type instanceof TObject) {
        return true;
    }

    if (typeDeclaration.type instanceof TStruct || typeDeclaration.type instanceof TUnion) {
        return terminatingTypeNames.has(typeDeclaration.type.name);
    }

    return true;
}

function structFieldsTerminate(
    fields: { [key: string]: TFieldDeclaration },
    terminatingTypeNames: Set<string>,
): boolean {
    return Object.values(fields).every(
        (field) => field.optional || typeDeclarationTerminates(field.typeDeclaration, terminatingTypeNames),
    );
}

function typeTerminates(type: TType, terminatingTypeNames: Set<string>): boolean {
    if (type instanceof TStruct) {
        return structFieldsTerminate(type.fields, terminatingTypeNames);
    }

    if (type instanceof TUnion) {
        return Object.values(type.tags).some((tag) => structFieldsTerminate(tag.fields, terminatingTypeNames));
    }

    return true;
}

export function validateTypeTermination(
    parsedTypes: { [key: string]: TType },
    schemaKeysToDocumentName: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    telepactSchemaDocumentNamesToJson: Record<string, string>,
): void {
    const terminatingTypeNames = new Set<string>();

    let changed = true;
    while (changed) {
        changed = false;
        for (const [typeName, type] of Object.entries(parsedTypes)) {
            if (terminatingTypeNames.has(typeName)) {
                continue;
            }

            if (typeTerminates(type, terminatingTypeNames)) {
                terminatingTypeNames.add(typeName);
                changed = true;
            }
        }
    }

    const parseFailures: SchemaParseFailure[] = [];
    for (const [schemaKey, documentName] of Object.entries(schemaKeysToDocumentName)) {
        if (schemaKey.startsWith('info.') || schemaKey.startsWith('headers.') || schemaKey.startsWith('errors.')) {
            continue;
        }

        const rootTypeNames = [schemaKey];
        if (schemaKey.startsWith('fn.')) {
            rootTypeNames.push(`${schemaKey}.->`);
        }

        for (const rootTypeName of rootTypeNames) {
            if (parsedTypes[rootTypeName] !== undefined && !terminatingTypeNames.has(rootTypeName)) {
                const path = rootTypeName.endsWith('.->')
                    ? [schemaKeysToIndex[schemaKey], '->']
                    : [schemaKeysToIndex[schemaKey], schemaKey];
                parseFailures.push(new SchemaParseFailure(documentName, path, 'RecursiveTypeUnterminated', {}));
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, telepactSchemaDocumentNamesToJson);
    }
}
