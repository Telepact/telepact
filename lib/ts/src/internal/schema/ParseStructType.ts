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

import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { VStruct } from '../types/VStruct';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructFields } from '../../internal/schema/ParseStructFields';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseStructType(
    path: any[],
    structDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    ctx: ParseContext,
): VStruct {
    const parseFailures: SchemaParseFailure[] = [];
    const otherKeys = new Set(Object.keys(structDefinitionAsPseudoJson));

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

    const fields = parseStructFields(thisPath, definition, ctx);

    return new VStruct(schemaKey, fields);
}
