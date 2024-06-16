import { UError } from 'uapi/internal/types/UError';
import { UStruct } from 'uapi/internal/types/UStruct';
import { UType } from 'uapi/internal/types/UType';
import { UUnion } from 'uapi/internal/types/UUnion';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { UFn } from 'uapi/internal/types/UFn';

export function applyErrorToParsedTypes(
    errorIndex: number,
    error: UError,
    parsedTypes: { [key: string]: UType },
    schemaKeysToIndex: { [key: string]: number },
): void {
    const parseFailures: SchemaParseFailure[] = [];

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

        for (const errorCaseName in errorCases) {
            const errorCase = errorCases[errorCaseName];
            const newKey = errorCaseName;
            const matcher = regex.exec(newKey);

            if (!matcher) {
                continue;
            }

            if (newKey in fnResultCases) {
                const otherPathIndex = schemaKeysToIndex[fnName];
                const errorCaseIndex = error.errors.caseIndices[newKey];
                const fnErrorCaseIndex = f.result.caseIndices[newKey];
                parseFailures.push(
                    new SchemaParseFailure(
                        [errorIndex, 'errors', errorCaseIndex, newKey],
                        'PathCollision',
                        { other: [otherPathIndex, '->', fnErrorCaseIndex, newKey] },
                        null,
                    ),
                );
            }

            fnResultCases[newKey] = errorCase;
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures);
    }
}
