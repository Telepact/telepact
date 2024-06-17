import { UApiSchema } from 'uapi/UApiSchema';
import { UType } from 'uapi/internal/types/UType';
import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { parseUapiSchema } from 'uapi/internal/schema/ParseUApiSchema';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';

export function newUapiSchema(uapiSchemaJson: string, typeExtensions: { [key: string]: UType }): UApiSchema {
    let uapiSchemaPseudoJsonInit: any;

    try {
        uapiSchemaPseudoJsonInit = JSON.parse(uapiSchemaJson);
    } catch (e) {
        throw new UApiSchemaParseError([new SchemaParseFailure([], 'JsonInvalid', {}, null)]);
    }

    if (!Array.isArray(uapiSchemaPseudoJsonInit)) {
        const thisParseFailure = getTypeUnexpectedParseFailure([], uapiSchemaPseudoJsonInit, 'Array');
        throw new UApiSchemaParseError(thisParseFailure);
    }

    const uapiSchemaPseudoJson = uapiSchemaPseudoJsonInit;

    return parseUapiSchema(uapiSchemaPseudoJson, typeExtensions, 0);
}
