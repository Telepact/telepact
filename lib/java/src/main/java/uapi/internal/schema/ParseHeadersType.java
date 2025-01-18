package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseTypeDeclaration.parseTypeDeclaration;

import java.util.List;
import java.util.Map;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFieldDeclaration;

public class ParseHeadersType {
    static UFieldDeclaration parseHeadersType(
            List<Object> path,
            Map<String, Object> headersDefinitionAsParsedJson,
            String schemaKey,
            String headerField,
            ParseContext ctx) {
        var typeDeclarationValue = headersDefinitionAsParsedJson.get(schemaKey);

        if (!(typeDeclarationValue instanceof List)) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(ctx.documentName, path, typeDeclarationValue, "Array"),
                    ctx.uApiSchemaDocumentNamesToJson);
        }
        final List<Object> typeDeclarationArray = (List<Object>) typeDeclarationValue;

        try {
            final var typeDeclaration = parseTypeDeclaration(
                    path, typeDeclarationArray, ctx);

            return new UFieldDeclaration(headerField, typeDeclaration, false);
        } catch (UApiSchemaParseError e) {
            throw new UApiSchemaParseError(e.schemaParseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }
    }
}
