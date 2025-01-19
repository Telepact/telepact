import { UError } from "../../internal/types/UError";
import { UType } from "../../internal/types/UType";
import { SchemaParseFailure } from "../../internal/schema/SchemaParseFailure";
import { UApiSchemaParseError } from "../../UApiSchemaParseError";
import { UFn } from "../../internal/types/UFn";
import { getPathDocumentCoordinatesPseudoJson } from "../../internal/schema/GetPathDocumentCoordinatesPseudoJson";

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
        const fnResultTags = fnResult.tags;
        const errorErrors = error.errors;
        const errorTags = errorErrors.tags;

        const matcher = regex.exec(errorKey);

        if (!matcher) {
            continue;
        }

        for (const errorTagName in errorTags) {
            const errorTag = errorTags[errorTagName];
            const newKey = errorTagName;

            if (newKey in fnResultTags) {
                const otherPathIndex = schemaKeysToIndex[fnName];
                const errorTagIndex = error.errors.tagIndices[newKey];
                const otherDocumentName = schemaKeysToDocumentNames[fnName];
                const fnErrorTagIndex = f.result.tagIndices[newKey];
                const otherPath = [otherPathIndex, "->", fnErrorTagIndex, newKey];
                const otherDocumentJson = documentNamesToJson[otherDocumentName];
                const otherLocation = getPathDocumentCoordinatesPseudoJson(otherPath, otherDocumentJson);
                parseFailures.push(
                    new SchemaParseFailure(
                        documentName,
                        [errorIndex, errorKey, errorTagIndex, newKey],
                        "PathCollision",
                        { document: otherDocumentName, path: otherPath, location: otherLocation },
                    ),
                );
            }

            fnResultTags[newKey] = errorTag;
        }
    }

    if (parseFailures.length > 0) {
        throw new UApiSchemaParseError(parseFailures, documentNamesToJson);
    }
}
