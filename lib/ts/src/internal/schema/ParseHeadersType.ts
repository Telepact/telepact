import { UApiSchemaParseError } from '../../UApiSchemaParseError';
import { getTypeUnexpectedParseFailure } from '../../internal/schema/GetTypeUnexpectedParseFailure';
import { parseTypeDeclaration } from '../../internal/schema/ParseTypeDeclaration';
import { UFieldDeclaration } from '../../internal/types/UFieldDeclaration';
import { ParseContext } from '../../internal/schema/ParseContext';

export function parseHeadersType(
    path: any[],
    headersDefinitionAsParsedJson: { [key: string]: any },
    schemaKey: string,
    headerField: string,
    ctx: ParseContext,
): UFieldDeclaration {
    const typeDeclarationValue = headersDefinitionAsParsedJson[schemaKey];

    if (!Array.isArray(typeDeclarationValue)) {
        throw new UApiSchemaParseError(
            getTypeUnexpectedParseFailure(ctx.documentName, path, typeDeclarationValue, 'Array'),
            ctx.uapiSchemaDocumentNamesToJson,
        );
    }

    const typeDeclarationArray = typeDeclarationValue;

    try {
        const typeDeclaration = parseTypeDeclaration(typeDeclarationArray, ctx);

        return new UFieldDeclaration(headerField, typeDeclaration, false);
    } catch (e) {
        throw new UApiSchemaParseError(e.schema_parse_failures, ctx.uapiSchemaDocumentNamesToJson);
    }
}
