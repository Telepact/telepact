//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TFieldDeclaration } from '../types/TFieldDeclaration.js';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { parseField } from '../../internal/schema/ParseField.js';
import { ParseContext } from '../../internal/schema/ParseContext.js';

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
