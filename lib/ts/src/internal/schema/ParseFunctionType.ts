import { UFn } from '../../internal/types/UFn';
import { UUnion } from '../../internal/types/UUnion';
import { UType } from '../../internal/types/UType';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructType } from '../../internal/schema/ParseStructType';
import { parseUnionType } from '../../internal/schema/ParseUnionType';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';

export function parseFunctionType(
    documentName: string,
    path: any[],
    functionDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    uApiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
    schemaKeysToDocumentName: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UFn {
    const parseFailures: SchemaParseFailure[] = [];

    let callType: UUnion | null = null;
    try {
        const argType = parseStructType(
            documentName,
            path,
            functionDefinitionAsParsedJson,
            schemaKey,
            ['->', '_errors'],
            uApiSchemaDocumentNamesToPseudoJson,
            schemaKeysToDocumentName,
            schemaKeysToIndex,
            parsedTypes,
            allParseFailures,
            failedTypes,
        );
        callType = new UUnion(schemaKey, { [schemaKey]: argType }, { [schemaKey]: 0 });
    } catch (e) {
        if (e instanceof UApiSchemaParseError) {
            parseFailures.push(...e.schemaParseFailures);
        } else {
            throw e;
        }
    }

    const resultSchemaKey = '->';

    const resPath = [...path, resultSchemaKey];

    let resultType: UUnion | null = null;
    if (!(resultSchemaKey in functionDefinitionAsParsedJson)) {
        parseFailures.push(new SchemaParseFailure(documentName, resPath, 'RequiredObjectKeyMissing', {}));
    } else {
        try {
            resultType = parseUnionType(
                documentName,
                path,
                functionDefinitionAsParsedJson,
                resultSchemaKey,
                Object.keys(functionDefinitionAsParsedJson),
                ['Ok_'],
                uApiSchemaDocumentNamesToPseudoJson,
                schemaKeysToDocumentName,
                schemaKeysToIndex,
                parsedTypes,
                allParseFailures,
                failedTypes,
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
        parseFailures.push(new SchemaParseFailure(documentName, regexPath, 'ObjectKeyDisallowed', {}));
    } else {
        const errorsRegexInit =
            errorsRegexKey in functionDefinitionAsParsedJson
                ? functionDefinitionAsParsedJson[errorsRegexKey]
                : '^errors\\..*$';

        if (typeof errorsRegexInit !== 'string') {
            const thisParseFailures = getTypeUnexpectedParseFailure(documentName, regexPath, errorsRegexInit, 'String');
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
