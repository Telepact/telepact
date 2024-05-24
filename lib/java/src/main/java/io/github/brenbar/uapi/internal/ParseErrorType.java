package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;

import static io.github.brenbar.uapi.internal.ParseUnionType.parseUnionType;
import static io.github.brenbar.uapi.internal.Append.append;

public class ParseErrorType {
    public static UError parseErrorType(Map<String, Object> errorDefinitionAsParsedJson,
            List<Object> uApiSchemaPseudoJson, int index, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
        final var schemaKey = "errors";
        final List<Object> basePath = List.of(index);

        final var parseFailures = new ArrayList<SchemaParseFailure>();

        final var otherKeys = new HashSet<>(errorDefinitionAsParsedJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = append(basePath, k);

                parseFailures.add(new SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var typeParameterCount = 0;

        final UUnion error = parseUnionType(basePath, errorDefinitionAsParsedJson, schemaKey, List.of(), List.of(),
                typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions,
                allParseFailures, failedTypes);

        return new UError(schemaKey, error);
    }
}
