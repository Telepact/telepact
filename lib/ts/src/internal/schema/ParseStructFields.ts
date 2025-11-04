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

import { TFieldDeclaration } from '../types/TFieldDeclaration';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { parseField } from '../../internal/schema/ParseField';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseStructFields(
    path: any[],
    referenceStruct: { [key: string]: any },
    isHeader: boolean,
    ctx: ParseContext,
): { [key: string]: TFieldDeclaration } {
    const parseFailures: SchemaParseFailure[] = [];
    const fields: { [key: string]: TFieldDeclaration } = {};

    for (const fieldDeclaration in referenceStruct) {
        for (const existingField in fields) {
            const existingFieldNoOpt = existingField.split('!')[0];
            const fieldNoOpt = fieldDeclaration.split('!')[0];
            if (fieldNoOpt === existingFieldNoOpt) {
                const structPath = [...path];
                parseFailures.push(
                    new SchemaParseFailure(ctx.documentName, structPath, 'DuplicateField', {
                        field: fieldNoOpt,
                    }),
                );
            }
        }

        try {
            const parsedField = parseField(path, fieldDeclaration, referenceStruct[fieldDeclaration], isHeader, ctx);
            const fieldName = parsedField.fieldName;
            fields[fieldName] = parsedField;
        } catch (e) {
            if (e instanceof TelepactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    return fields;
}
