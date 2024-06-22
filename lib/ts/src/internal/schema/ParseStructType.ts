import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UType } from 'uapi/internal/types/UType';
import { getTypeUnexpectedParseFailure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructFields } from 'uapi/internal/schema/ParseStructFields';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';

export function parseStructType(
    path: any[],
    structDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    typeParameterCount: number,
    uapiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    typeExtensions: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UStruct {
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
            parseFailures.push(new SchemaParseFailure(loopPath, 'ObjectKeyDisallowed', {}, null));
        }
    }

    const thisPath = [...path, schemaKey];
    const defInit = structDefinitionAsPseudoJson[schemaKey];

    let definition: { [key: string]: any } | null = null;
    if (typeof defInit !== 'object' || defInit === null) {
        const branchParseFailures = getTypeUnexpectedParseFailure(thisPath, defInit, 'Object');
        parseFailures.push(...branchParseFailures);
    } else {
        definition = defInit;
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    const fields = parseStructFields(
        definition,
        thisPath,
        typeParameterCount,
        uapiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes,
    );

    return new UStruct(schemaKey, fields, typeParameterCount);
}
