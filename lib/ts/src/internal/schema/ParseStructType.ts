//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { TStruct } from '../types/TStruct.js';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure.js';
import { parseStructFields } from '../../internal/schema/ParseStructFields.js';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { ParseContext } from '../../internal/schema/ParseContext.js';

export function parseStructType(
    path: any[],
    structDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    ctx: ParseContext,
): TStruct {
    const parseFailures: SchemaParseFailure[] = [];
    const otherKeys = new Set(Object.keys(structDefinitionAsPseudoJson).filter((key) => !key.startsWith('$')));

    otherKeys.delete(schemaKey);
    otherKeys.delete('///');
    otherKeys.delete('_ignoreIfDuplicate');
    for (const ignoreKey of ignoreKeys) {
        otherKeys.delete(ignoreKey);
    }

    if (otherKeys.size > 0) {
        for (const k of otherKeys) {
            const loopPath = [...path, k];
            parseFailures.push(new SchemaParseFailure(ctx.documentName, loopPath, 'ObjectKeyDisallowed', {}));
        }
    }

    const thisPath = [...path, schemaKey];
    const defInit = structDefinitionAsPseudoJson[schemaKey];

    let definition: { [key: string]: any } | null = null;
    if (typeof defInit !== 'object' || Array.isArray(defInit) || defInit === null || defInit === undefined) {
        const branchParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, thisPath, defInit, 'Object');
        parseFailures.push(...branchParseFailures);
    } else {
        definition = defInit;
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    const isHeader = false;
    const fields = parseStructFields(thisPath, definition, isHeader, ctx);

    return new TStruct(schemaKey, fields);
}
