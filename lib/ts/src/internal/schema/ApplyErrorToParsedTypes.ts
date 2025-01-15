import { UError } from '../../internal/types/UError';
import { UType } from '../../internal/types/UType';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { UFn } from '../../internal/types/UFn';
import { getPathDocumentCoordinatesPseudoJson } from '../../internal/schema/GetPathDocumentCoordinatesPseudoJson';

export function applyErrorToParsedTypes(
    error: UError,
    parsedTypes: { [key: string]: UType },
    schemaKeysToDocumentNames: { [key: string]: string },
    schemaKeysToIndex: { [key: string]: number },
    documentNamesToJson: { [key: string]: string },
): void {
    const parseFailures: SchemaParseFailure[] = [];

    const errorKey = error.name;
    const errorIndex = schemaKeysToIndex[errorKey];
    const documentName = schemaKeysToDocumentNames[errorKey];

    for (const parsedTypeName in parsedTypes) {
        const parsedType = parsedTypes[parsedTypeName];

        if (!(parsedType instanceof UFn)) {
            continue;
        }

        const f = parsedType;
        const fnName = f.name;
        const regex = new RegExp(f.errorsRegex);
        const fnResult = f.result;
        const fnResultCases = fnResult.cases;
        const errorErrors = error.errors;
        const errorCases = errorErrors.cases;

        const matcher = regex.exec(errorKey);

        if (!matcher) {
            continue;
        }

        for (const errorCaseName in errorCases) {
            const errorCase = errorCases[errorCaseName];
            const newKey = errorCaseName;

            if (newKey in fnResultCases) {
                const otherPathIndex = schemaKeysToIndex[fnName];
                const errorCaseIndex = error.errors.caseIndices[newKey];
                const otherDocumentName = schemaKeysToDocumentNames[fnName];
                const fnErrorCaseIndex = f.result.caseIndices[newKey];
                const otherPath = [otherPathIndex, '->', fnErrorCaseIndex, newKey];
                const otherDocumentJson = documentNamesToJson[otherDocumentName];
                const otherLocation = getPathDocumentCoordinatesPseudoJson(otherPath, otherDocumentJson);
                parseFailures.push(
                    new SchemaParseFailure(
                        documentName,
                        [errorIndex, errorKey, errorCaseIndex, newKey],
                        'PathCollision',
                        { document: otherDocumentName, path: otherPath, location: otherLocation },
                    ),
                );
            }

            fnResultCases[newKey] = errorCase;
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, documentNamesToJson);
    }
}
