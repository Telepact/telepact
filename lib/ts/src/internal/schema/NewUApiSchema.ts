import { UApiSchema } from '../../UApiSchema';
import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseUapiSchema } from '../../internal/schema/ParseUApiSchema';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';

export function newUapiSchema(uApiSchemaFilesToJson: Record<string, string>): UApiSchema {
    const finalPseudoJson: Record<string, any[]> = {};

    for (const [documentName, jsonValue] of Object.entries(uApiSchemaFilesToJson)) {
        let uApiSchemaPseudoJsonInit: any;
        try {
            uApiSchemaPseudoJsonInit = JSON.parse(jsonValue);
        } catch (e) {
            throw new UApiSchemaParseError([new SchemaParseFailure(documentName, [], 'JsonInvalid', {})], e as Error);
        }

        if (!Array.isArray(uApiSchemaPseudoJsonInit)) {
            const thisParseFailure = getTypeUnexpectedParseFailure(documentName, [], uApiSchemaPseudoJsonInit, 'Array');
            throw new UApiSchemaParseError(thisParseFailure);
        }
        const uApiSchemaPseudoJson: any[] = uApiSchemaPseudoJsonInit;

        finalPseudoJson[documentName] = uApiSchemaPseudoJson;
    }

    return parseUapiSchema(finalPseudoJson);
}
