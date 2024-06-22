import { UApiSchema } from 'uapi/UApiSchema';
import { UType } from 'uapi/internal/types/UType';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { parseUapiSchema } from 'uapi/internal/schema/ParseUApiSchema';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';

export function extendUapiSchema(
    first: UApiSchema,
    secondUapiSchemaJson: string,
    secondTypeExtensions: { [key: string]: UType },
): UApiSchema {
    let secondUapiSchemaPseudoJsonInit;
    try {
        secondUapiSchemaPseudoJsonInit = JSON.parse(secondUapiSchemaJson);
    } catch (e) {
        throw new UApiSchemaParseError([new SchemaParseFailure([], 'JsonInvalid', {}, null)], e);
    }

    if (!Array.isArray(secondUapiSchemaPseudoJsonInit)) {
        const thisParseFailure = getTypeUnexpectedParseFailure([], secondUapiSchemaPseudoJsonInit, 'Array');
        throw new UApiSchemaParseError(thisParseFailure);
    }

    const secondUapiSchemaPseudoJson = secondUapiSchemaPseudoJsonInit;

    const firstOriginal = first.original;
    const firstTypeExtensions = first.typeExtensions;

    const original = firstOriginal.concat(secondUapiSchemaPseudoJson);

    const typeExtensions = { ...firstTypeExtensions, ...secondTypeExtensions };

    return parseUapiSchema(original, typeExtensions, firstOriginal.length);
}
