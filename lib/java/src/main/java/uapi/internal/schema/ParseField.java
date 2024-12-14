package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseTypeDeclaration.parseTypeDeclaration;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;

public class ParseField {
    static UFieldDeclaration parseField(String documentName, List<Object> path, String fieldDeclaration,
            Object typeDeclarationValue,
            int typeParameterCount, Map<String, List<Object>> uApiSchemaDocumentNamesToPseudoJson,
            Map<String, String> schemaKeysToDocumentName,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var regexString = "^([a-z][a-zA-Z0-9_]*)(!)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            final List<Object> finalPath = new ArrayList<>(path);
            finalPath.add(fieldDeclaration);

            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(documentName, finalPath,
                    "KeyRegexMatchFailed", Map.of("regex", regexString))));
        }

        final var fieldName = matcher.group(0);
        final var optional = matcher.group(2) != null;

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(fieldName);

        if (!(typeDeclarationValue instanceof List)) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(documentName, thisPath, typeDeclarationValue, "Array"));
        }
        final List<Object> typeDeclarationArray = (List<Object>) typeDeclarationValue;

        final var typeDeclaration = parseTypeDeclaration(documentName, thisPath,
                typeDeclarationArray, typeParameterCount,
                uApiSchemaDocumentNamesToPseudoJson,
                schemaKeysToDocumentName,
                schemaKeysToIndex,
                parsedTypes,
                allParseFailures, failedTypes);

        return new UFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
