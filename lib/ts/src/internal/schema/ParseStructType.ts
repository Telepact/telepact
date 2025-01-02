import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UStruct } from '../../internal/types/UStruct';
import { UType } from '../../internal/types/UType';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseStructFields } from '../../internal/schema/ParseStructFields';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';

export function parseStructType(
    documentName: string,
    path: any[],
    structDefinitionAsPseudoJson: { [key: string]: any },
    schemaKey: string,
    ignoreKeys: string[],
    uapiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
    schemaKeysToDocumentName: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
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
            parseFailures.push(new SchemaParseFailure(documentName, loopPath, 'ObjectKeyDisallowed', {}));
        }
    }

    const thisPath = [...path, schemaKey];
    const defInit = structDefinitionAsPseudoJson[schemaKey];

    let definition: { [key: string]: any } | null = null;
    if (typeof defInit !== 'object' || Array.isArray(defInit) || defInit === null || defInit === undefined) {
        const branchParseFailures = getTypeUnexpectedParseFailure(documentName, thisPath, defInit, 'Object');
        parseFailures.push(...branchParseFailures);
    } else {
        definition = defInit;
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    const fields = parseStructFields(
        definition,
        documentName,
        thisPath,
        uapiSchemaDocumentNamesToPseudoJson,
        schemaKeysToDocumentName,
        schemaKeysToIndex,
        parsedTypes,
        allParseFailures,
        failedTypes,
    );

    return new UStruct(schemaKey, fields);
}
