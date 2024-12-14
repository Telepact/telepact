package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseStructFields.parseStructFields;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;

public class ParseStructType {
    static UStruct parseStructType(String documentName, List<Object> path,
            Map<String, Object> structDefinitionAsPseudoJson,
            String schemaKey, List<String> ignoreKeys, int typeParameterCount,
            Map<String, List<Object>> uApiSchemaDocumentNamesToPseudoJson, Map<String, String> schemaKeysToDocumentName,
            Map<String, Integer> schemaKeysToIndex, Map<String, UType> parsedTypes,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var otherKeys = new HashSet<>(structDefinitionAsPseudoJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");
        otherKeys.remove("_ignoreIfDuplicate");
        for (final var ignoreKey : ignoreKeys) {
            otherKeys.remove(ignoreKey);
        }

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = new ArrayList<>(path);
                loopPath.add(k);

                parseFailures.add(new SchemaParseFailure(documentName, loopPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(schemaKey);

        final Object defInit = structDefinitionAsPseudoJson.get(schemaKey);

        Map<String, Object> definition = null;
        if (!(defInit instanceof Map)) {
            final List<SchemaParseFailure> branchParseFailures = getTypeUnexpectedParseFailure(documentName, thisPath,
                    defInit, "Object");

            parseFailures.addAll(branchParseFailures);
        } else {
            definition = (Map<String, Object>) defInit;
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var fields = parseStructFields(definition, documentName, thisPath, typeParameterCount,
                uApiSchemaDocumentNamesToPseudoJson, schemaKeysToDocumentName, schemaKeysToIndex, parsedTypes,
                allParseFailures,
                failedTypes);

        return new UStruct(schemaKey, fields, typeParameterCount);
    }
}
