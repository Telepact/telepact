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

import { VFn } from '../types/VFn';
import { VUnion } from '../types/VUnion';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError';
import { ParseContext } from '../../internal/schema/ParseContext';
import { getOrParseType } from './GetOrParseType';
import { derivePossibleSelect } from './DerivePossibleSelect';
import { VSelect } from '../types/VSelect';

export function parseFunctionType(
    path: any[],
    functionDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): VFn {
    const parseFailures: SchemaParseFailure[] = [];

    let callType: VUnion | null = null;
    try {
        const argType = parseStructType(path, functionDefinitionAsParsedJson, schemaKey, ['->', '_errors'], ctx);
        callType = new VUnion(schemaKey, { [schemaKey]: argType }, { [schemaKey]: 0 });
    } catch (e) {
        if (e instanceof TelepactSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    const resultSchemaKey = '->';

    let resultType: VUnion | null = null;
    if (!(resultSchemaKey in functionDefinitionAsParsedJson)) {
        parseFailures.push(
            new SchemaParseFailure(ctx.documentName, path, 'RequiredObjectKeyMissing', { key: resultSchemaKey }),
        );
    } else {
        try {
            resultType = parseUnionType(
                path,
                functionDefinitionAsParsedJson,
                resultSchemaKey,
                Object.keys(functionDefinitionAsParsedJson),
                ['Ok_'],
                ctx,
            );
        } catch (e) {
            if (e instanceof TelepactSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            } else {
                throw e;
            }
        }
    }

    const errorsRegexKey = '_errors';

    const regexPath = [...path, errorsRegexKey];

    let errorsRegex: string | null = null;
    if (errorsRegexKey in functionDefinitionAsParsedJson && !schemaKey.endsWith('_')) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, regexPath, 'ObjectKeyDisallowed', {}));
    } else {
        const errorsRegexInit =
            errorsRegexKey in functionDefinitionAsParsedJson
                ? functionDefinitionAsParsedJson[errorsRegexKey]
                : '^errors\\..*$';

        if (typeof errorsRegexInit !== 'string') {
            const thisParseFailures = getTypeUnexpectedParseFailure(
                ctx.documentName,
                regexPath,
                errorsRegexInit,
                'String',
            );
            parseFailures.push(...thisParseFailures);
        } else {
            errorsRegex = errorsRegexInit;
        }
    }

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    const fnSelectType = derivePossibleSelect(schemaKey, resultType as VUnion);
    const selectType = getOrParseType([], '_ext.Select_', ctx) as VSelect;
    selectType.possibleSelects[schemaKey] = fnSelectType;

    return new VFn(schemaKey, callType as VUnion, resultType as VUnion, errorsRegex as string);
}
