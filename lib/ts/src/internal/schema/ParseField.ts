//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { TFieldDeclaration } from '../types/TFieldDeclaration.js';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure.js';
import { ParseContext } from '../../internal/schema/ParseContext.js';
import { parseTypeDeclaration } from './ParseTypeDeclaration.js';

export function parseField(
    path: any[],
    fieldDeclaration: string,
    typeDeclarationValue: any,
    isHeader: boolean,
    ctx: ParseContext,
): TFieldDeclaration {
    const headerRegexString = '^@[a-z][a-zA-Z0-9_]*$';
    const regexString = '^([a-z][a-zA-Z0-9_]*)(!)?$';
    const regexToUse = isHeader ? headerRegexString : regexString;
    const regex = new RegExp(regexToUse);

    const matcher = fieldDeclaration.match(regex);
    if (!matcher) {
        const finalPath = [...path, fieldDeclaration];
        throw new TelepactSchemaParseError(
            [new SchemaParseFailure(ctx.documentName, finalPath, 'KeyRegexMatchFailed', { regex: regexToUse })],
            ctx.telepactSchemaDocumentNamesToJson,
        );
    }

    const fieldName = matcher[0];
    const optional = isHeader ? true : Boolean(matcher[2]);

    const thisPath = [...path, fieldName];

    const typeDeclaration = parseTypeDeclaration(thisPath, typeDeclarationValue, ctx);

    return new TFieldDeclaration(fieldName, typeDeclaration, optional);
}
