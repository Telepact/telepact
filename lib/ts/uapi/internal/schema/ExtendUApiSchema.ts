import { UApiSchema } from 'uapi/UApiSchema';
import { UType } from 'uapi/internal/types/UType';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { get_type_unexpected_parse_failure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { parse_uapi_schema } from 'uapi/internal/schema/ParseUApiSchema';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import * as json from 'json';

export function extendUapiSchema(
    first: UApiSchema,
    secondUapiSchemaJson: string,
    secondTypeExtensions: { [key: string]: UType },
): UApiSchema {
    let secondUapiSchemaPseudoJsonInit;
    try {
        secondUapiSchemaPseudoJsonInit = json.loads(secondUapiSchemaJson);
    } catch (e) {
        throw new UApiSchemaParseError([new SchemaParseFailure([], 'JsonInvalid', {}, null)], e);
    }

    if (!Array.isArray(secondUapiSchemaPseudoJsonInit)) {
        const thisParseFailure = get_type_unexpected_parse_failure([], secondUapiSchemaPseudoJsonInit, 'Array');
        throw new UApiSchemaParseError(thisParseFailure);
    }

    const secondUapiSchemaPseudoJson = secondUapiSchemaPseudoJsonInit;

    const firstOriginal = first.original;
    const firstTypeExtensions = first.typeExtensions;

    const original = firstOriginal.concat(secondUapiSchemaPseudoJson);

    const typeExtensions = { ...firstTypeExtensions, ...secondTypeExtensions };

    return parse_uapi_schema(original, typeExtensions, firstOriginal.length);
}
