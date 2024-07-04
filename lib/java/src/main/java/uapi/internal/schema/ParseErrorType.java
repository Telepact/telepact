package uapi.internal.schema;

import static uapi.internal.schema.ParseUnionType.parseUnionType;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UError;
import uapi.internal.types.UType;
import uapi.internal.types.UUnion;

public class ParseErrorType {
    public static UError parseErrorType(Map<String, Object> errorDefinitionAsParsedJson,
            List<Object> uApiSchemaPseudoJson, int index, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        final var schemaKey = "errors";
        final List<Object> basePath = List.of(index);

        final var parseFailures = new ArrayList<SchemaParseFailure>();

        final var otherKeys = new HashSet<>(errorDefinitionAsParsedJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = new ArrayList<>(basePath);
                loopPath.add(k);

                parseFailures.add(new SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var typeParameterCount = 0;

        final UUnion error = parseUnionType(basePath, errorDefinitionAsParsedJson, schemaKey, List.of(), List.of(),
                typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                allParseFailures, failedTypes);

        return new UError(schemaKey, error);
    }
}
