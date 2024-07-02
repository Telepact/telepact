import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseTypeDeclaration } from '../../internal/schema/ParseTypeDeclaration';
import { SchemaParseFailure } from '../../internal/schema/SchemaParseFailure';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { UType } from '../../internal/types/UType';

export function parseHeadersType(
    headersDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    headerField: string,
    index: number,
    uapiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UFieldDeclaration {
    const path = [index, schemaKey];

    const typeDeclarationValue = headersDefinitionAsParsedJson[schemaKey];

    if (!Array.isArray(typeDeclarationValue)) {
        throw new UApiSchemaParseError(getTypeUnexpectedParseFailure(path, typeDeclarationValue, 'Array'));
    }

    const typeDeclarationArray = typeDeclarationValue;

    const typeParameterCount = 0;

    try {
        const typeDeclaration = parseTypeDeclaration(
            path,
            typeDeclarationArray,
            typeParameterCount,
            uapiSchemaPseudoJson,
            schemaKeysToIndex,
            parsedTypes,
            allParseFailures,
            failedTypes,
        );

        return new UFieldDeclaration(headerField, typeDeclaration, false);
    } catch (e) {
        throw new UApiSchemaParseError(e.schema_parse_failures);
    }
}
