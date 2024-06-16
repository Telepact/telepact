import { UApiSchemaParseError } from 'uapi/UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from 'uapi/internal/schema/GetTypeUnexpectedParseFailure';
import { parseTypeDeclaration } from 'uapi/internal/schema/ParseTypeDeclaration';
import { SchemaParseFailure } from 'uapi/internal/schema/SchemaParseFailure';
import { UFieldDeclaration } from 'uapi/internal/types/UFieldDeclaration';
import { UType } from 'uapi/internal/types/UType';

export function parseHeadersType(
    headersDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    headerField: string,
    index: number,
    uapiSchemaPseudoJson: any[],
    schemaKeysToIndex: { [key: string]: number },
    parsedTypes: { [key: string]: UType },
    typeExtensions: { [key: string]: UType },
    allParseFailures: SchemaParseFailure[],
    failedTypes: Set<string>,
): UFieldDeclaration {
    const path = [index, schemaKey];

    const typeDeclarationValue = headersDefinitionAsParsedJson[schemaKey];

    if (!Array.isArray(typeDeclarationValue)) {
        throw new UApiSchemaParseError(get_type_unexpected_parse_failure(path, typeDeclarationValue, 'Array'));
    }

    const typeDeclarationArray = typeDeclarationValue;

    const typeParameterCount = 0;

    try {
        const typeDeclaration = parse_type_declaration(
            path,
            typeDeclarationArray,
            typeParameterCount,
            uapiSchemaPseudoJson,
            schemaKeysToIndex,
            parsedTypes,
            typeExtensions,
            allParseFailures,
            failedTypes,
        );

        return new UFieldDeclaration(headerField, typeDeclaration, false);
    } catch (e) {
        throw new UApiSchemaParseError(e.schema_parse_failures);
    }
}
