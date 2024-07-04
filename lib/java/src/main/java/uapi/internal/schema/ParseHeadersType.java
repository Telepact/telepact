package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseTypeDeclaration.parseTypeDeclaration;

import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;

public class ParseHeadersType {
    static UFieldDeclaration parseHeadersType(Map<String, Object> headersDefinitionAsParsedJson, String schemaKey,
            String headerField,
            int index, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final List<Object> path = List.of(index, schemaKey);

        var typeDeclarationValue = headersDefinitionAsParsedJson.get(schemaKey);

        if (!(typeDeclarationValue instanceof List)) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(path, typeDeclarationValue, "Array"));
        }
        final List<Object> typeDeclarationArray = (List<Object>) typeDeclarationValue;

        final var typeParameterCount = 0;

        try {
            final var typeDeclaration = parseTypeDeclaration(path,
                    typeDeclarationArray, typeParameterCount,
                    uApiSchemaPseudoJson,
                    schemaKeysToIndex,
                    parsedTypes,
                    allParseFailures, failedTypes);

            return new UFieldDeclaration(headerField, typeDeclaration, false);
        } catch (UApiSchemaParseError e) {
            throw new UApiSchemaParseError(e.schemaParseFailures);
        }
    }
}
