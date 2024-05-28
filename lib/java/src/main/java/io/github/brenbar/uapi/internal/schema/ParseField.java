package io.github.brenbar.uapi.internal.schema;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UFieldDeclaration;
import io.github.brenbar.uapi.internal.types.UType;

import static io.github.brenbar.uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.schema.ParseTypeDeclaration.parseTypeDeclaration;

public class ParseField {
    static UFieldDeclaration parseField(List<Object> path, String fieldDeclaration, Object typeDeclarationValue,
            int typeParameterCount, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var regexString = "^([a-z][a-zA-Z0-9_]*)(!)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            final List<Object> finalPath = new ArrayList<>(path);
            finalPath.add(fieldDeclaration);

            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(finalPath,
                    "KeyRegexMatchFailed", Map.of("regex", regexString), null)));
        }

        final var fieldName = matcher.group(0);
        final var optional = matcher.group(2) != null;

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(fieldName);

        if (!(typeDeclarationValue instanceof List)) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(thisPath, typeDeclarationValue, "Array"));
        }
        final List<Object> typeDeclarationArray = (List<Object>) typeDeclarationValue;

        final var typeDeclaration = parseTypeDeclaration(thisPath,
                typeDeclarationArray, typeParameterCount,
                uApiSchemaPseudoJson,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions, allParseFailures, failedTypes);

        return new UFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
