import { UApiSchema } from '../../UApiSchema';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseUapiSchema } from '../../internal/schema/ParseUApiSchema';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';

export function newUapiSchema(uapiSchemaJson: string): UApiSchema {
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

    return parseUapiSchema(uapiSchemaPseudoJson, 0);
}
