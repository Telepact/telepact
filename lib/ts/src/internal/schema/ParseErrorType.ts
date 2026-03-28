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
import { TError } from '../types/TError';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { ParseContext } from '../../internal/schema/ParseContext';

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
