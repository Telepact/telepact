package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;

import static io.github.brenbar.uapi.internal.ParseTypeDeclaration.parseTypeDeclaration;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.AsList.asList;

public class ParseHeadersType {
    static _UFieldDeclaration parseHeadersType(Map<String, Object> headersDefinitionAsParsedJson, String schemaKey,
            String headerField,
            int index, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final List<Object> path = List.of(index, schemaKey);

        var typeDeclarationValue = headersDefinitionAsParsedJson.get(schemaKey);

        final List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = asList(typeDeclarationValue);
        } catch (ClassCastException e) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(path, typeDeclarationValue, "Array"));
        }

        final var typeParameterCount = 0;

        try {
            final var typeDeclaration = parseTypeDeclaration(path,
                    typeDeclarationArray, typeParameterCount,
                    uApiSchemaPseudoJson,
                    schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions, allParseFailures, failedTypes);

            return new _UFieldDeclaration(headerField, typeDeclaration, false);
        } catch (UApiSchemaParseError e) {
            throw new UApiSchemaParseError(e.schemaParseFailures);
        }
    }
}
