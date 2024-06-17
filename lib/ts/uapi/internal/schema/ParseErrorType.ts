import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UError } from 'uapi/internal/types/UError';
import { UType } from 'uapi/internal/types/UType';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { parseUnionType } from './ParseUnionType';

export function parseErrorType(
    errorDefinitionAsParsedJson: { [key: string]: any },
    uApiSchemaPseudoJson: any[],
    index: number,
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    typeExtensions: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UError {
    const schemaKey = 'errors';
    const basePath: any[] = [index];

    const parseFailures: SchemaParseFailure[] = [];

    const otherKeys = Object.keys(errorDefinitionAsParsedJson).filter((key) => key !== schemaKey && key !== '///');

    if (otherKeys.length > 0) {
        for (const k of otherKeys) {
            const loopPath = basePath.concat(k);
            parseFailures.push(new SchemaParseFailure(loopPath as any[], 'ObjectKeyDisallowed', {}, null));
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }

    const typeParameterCount = 0;

    const error = parseUnionType(
        basePath,
        errorDefinitionAsParsedJson,
        schemaKey,
        [],
        [],
        typeParameterCount,
        uApiSchemaPseudoJson,
        schemaKeysToIndex,
        parsedTypes,
        typeExtensions,
        allParseFailures,
        failedTypes,
    );

    return new UError(schemaKey, error);
}
