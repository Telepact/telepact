import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UError } from '../../internal/types/UError';
import { UType } from '../../internal/types/UType';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { parseUnionType } from './ParseUnionType';

export function parseErrorType(
    errorDefinitionAsParsedJson: { [key: string]: any },
    documentName: string,
    uApiSchemaDocumentNamesToPseudoJson: { [key: string]: any[] },
    schemaKey: string,
    index: number,
    schemaKeysToDocumentName: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UError {
    const basePath: any[] = [index];

    const parseFailures: SchemaParseFailure[] = [];

    const otherKeys = Object.keys(errorDefinitionAsParsedJson).filter((key) => key !== schemaKey && key !== '///');

    if (otherKeys.length > 0) {
        for (const k of otherKeys) {
            const loopPath = basePath.concat(k);
            parseFailures.push(new SchemaParseFailure(documentName, loopPath as any[], 'ObjectKeyDisallowed', {}));
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    const error = parseUnionType(
        documentName,
        basePath,
        errorDefinitionAsParsedJson,
        schemaKey,
        [],
        [],
        uApiSchemaDocumentNamesToPseudoJson,
        schemaKeysToDocumentName,
        schemaKeysToIndex,
        parsedTypes,
        allParseFailures,
        failedTypes,
    );

    return new UError(schemaKey, error);
}
