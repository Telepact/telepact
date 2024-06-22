import { UFn } from '../../internal/types/UFn';
import { UUnion } from '../../internal/types/UUnion';
import { UType } from '../../internal/types/UType';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';

export function parseFunctionType(
    path: any[],
    functionDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    uApiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    typeExtensions: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UFn {
    const parseFailures: SchemaParseFailure[] = [];
    const typeParameterCount = 0;

    let callType: UUnion | null = null;
    try {
        const argType = parseStructType(
            path,
            functionDefinitionAsParsedJson,
            schemaKey,
            ['->', '_errors'],
            typeParameterCount,
            uApiSchemaPseudoJson,
            schemaKeysToIndex,
            parsedTypes,
            typeExtensions,
            allParseFailures,
            failedTypes,
        );
        callType = new UUnion(schemaKey, { [schemaKey]: argType }, { [schemaKey]: 0 }, typeParameterCount);
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        }
    }

    const resultSchemaKey = '->';

    const resPath = [...path, resultSchemaKey];

    let resultType: UUnion | null = null;
    if (!(resultSchemaKey in functionDefinitionAsParsedJson)) {
        parseFailures.push(new SchemaParseFailure(resPath, 'RequiredObjectKeyMissing', {}, null));
    } else {
        try {
            resultType = parseUnionType(
                path,
                functionDefinitionAsParsedJson,
                resultSchemaKey,
                Object.keys(functionDefinitionAsParsedJson),
                ['Ok_'],
                typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions,
                allParseFailures,
                failedTypes,
            );
        } catch (e) {
            if (e instanceof UApiSchemaParseError) {
                parseFailures.push(...e.schemaParseFailures);
            }
        }
    }

    const errorsRegexKey = '_errors';

    const regexPath = [...path, errorsRegexKey];

    let errorsRegex: string | null = null;
    if (errorsRegexKey in functionDefinitionAsParsedJson && !schemaKey.endsWith('_')) {
        parseFailures.push(new SchemaParseFailure(regexPath, 'ObjectKeyDisallowed', {}, null));
    } else {
        const errorsRegexInit = functionDefinitionAsParsedJson[errorsRegexKey] || '^.*$';

        if (typeof errorsRegexInit !== 'string') {
            const thisParseFailures = getTypeUnexpectedParseFailure(regexPath, errorsRegexInit, 'String');
            parseFailures.push(...thisParseFailures);
        } else {
            errorsRegex = errorsRegexInit;
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    return new UFn(schemaKey, callType as UUnion, resultType as UUnion, errorsRegex as string);
}
