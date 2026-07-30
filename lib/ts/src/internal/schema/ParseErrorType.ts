//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { TError } from '../types/TError.js';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { parseUnionType } from '../../internal/schema/ParseUnionType.js';
import { ParseContext } from '../../internal/schema/ParseContext.js';

export function parseErrorType(
    path: any[],
    errorDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): TError {
    const parseFailures: SchemaParseFailure[] = [];

    const otherKeys = Object.keys(errorDefinitionAsParsedJson).filter((key) => key !== schemaKey && key !== '///');

    if (otherKeys.length > 0) {
        for (const k of otherKeys) {
            const loopPath = path.concat(k);
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath as any[], 'ObjectKeyDisallowed', {}));
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    const error = parseUnionType(path, errorDefinitionAsParsedJson, schemaKey, [], [], ctx);

    return new TError(schemaKey, error);
}
