import { UFn } from '../../internal/types/UFn';
import { UUnion } from '../../internal/types/UUnion';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { ParseContext } from '../../internal/schema/ParseContext';
import { getOrParseType } from './GetOrParseType';
import { derivePossibleSelect } from './DerivePossibleSelect';
import { USelect } from '../types/USelect';

export function parseFunctionType(
    path: any[],
    functionDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    ctx: ParseContext,
): UFn {
    const parseFailures: SchemaParseFailure[] = [];

    let callType: UUnion | null = null;
    try {
        const argType = parseStructType(path, functionDefinitionAsParsedJson, schemaKey, ['->', '_errors'], ctx);
        callType = new UUnion(schemaKey, { [schemaKey]: argType }, { [schemaKey]: 0 });
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    const resultSchemaKey = '->';

    let resultType: UUnion | null = null;
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
            if (e instanceof UApiSchemaParseError) {
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
        throw new UApiSchemaParseError(parseFailures, ctx.uapiSchemaDocumentNamesToJson);
    }

    const fnSelectType = derivePossibleSelect(schemaKey, resultType as UUnion);
    const selectType = getOrParseType(path, '_ext.Select_', ctx) as USelect;
    selectType.possibleSelects[schemaKey] = fnSelectType;

    return new UFn(schemaKey, callType as UUnion, resultType as UUnion, errorsRegex as string);
}
