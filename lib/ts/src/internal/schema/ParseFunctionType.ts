//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

import { TUnion } from '../types/TUnion.js';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure.js';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure.js';
import { parseStructType } from '../../internal/schema/ParseStructType.js';
import { parseUnionType } from '../../internal/schema/ParseUnionType.js';
import { TelepactSchemaParseError } from '../../TelepactSchemaParseError.js';
import { ParseContext } from '../../internal/schema/ParseContext.js';
import { getOrParseType } from './GetOrParseType.js';
import { derivePossibleSelect } from './DerivePossibleSelect.js';
import { TSelect } from '../types/TSelect.js';

export function parseFunctionResultType(
    path: any[],
    functionDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): TUnion {
    const parseFailures: SchemaParseFailure[] = [];

    const resultSchemaKey = '->';

    let resultType: TUnion | null = null;
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

    if (parseFailures.length > 0) {
        throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
    }

    const fnSelectType = derivePossibleSelect(schemaKey, resultType as TUnion);

    const selectType = getOrParseType([], '_ext.Select_', ctx) as TSelect;
    selectType.possibleSelects[schemaKey] = fnSelectType;

    return resultType;
}

export function parseFunctionErrorsRegex(
    path: any[],
    functionDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,    
): string {
    const parseFailures: SchemaParseFailure[] = [];

    const errorsRegexKey = '_errors';
    const isInternal = schemaKey.endsWith('_') || functionDefinitionAsParsedJson['$internal'] === true;

    const regexPath = [...path, errorsRegexKey];

    let errorsRegex: string | null = null;
    if (errorsRegexKey in functionDefinitionAsParsedJson && !isInternal) {
        parseFailures.push(new SchemaParseFailure(ctx.documentName, regexPath, 'ObjectKeyDisallowed', {}));
    } else {
        const errorsRegexInit =
            errorsRegexKey in functionDefinitionAsParsedJson
                ? functionDefinitionAsParsedJson[errorsRegexKey]
                : isInternal
                  ? '^errors\\.Validation_$'
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

    return errorsRegex;
}
