package io.github.brenbar.uapi.internal.schema;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UType;

import static io.github.brenbar.uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.schema.ParseStructFields.parseStructFields;

public class ParseStructType {
    static UStruct parseStructType(List<Object> path, Map<String, Object> structDefinitionAsPseudoJson,
            String schemaKey, List<String> ignoreKeys, int typeParameterCount, List<Object> uApiSchemaPseudoJson,
            Map<String, Integer> schemaKeysToIndex, Map<String, UType> parsedTypes,
            Map<String, UType> typeExtensions,
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

                parseFailures.add(new SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(schemaKey);

        final Object defInit = structDefinitionAsPseudoJson.get(schemaKey);

        Map<String, Object> definition = null;
        if (!(defInit instanceof Map)) {
            final List<SchemaParseFailure> branchParseFailures = getTypeUnexpectedParseFailure(thisPath,
                    defInit, "Object");

            parseFailures.addAll(branchParseFailures);
        } else {
            definition = (Map<String, Object>) defInit;
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var fields = parseStructFields(definition, thisPath, typeParameterCount,
                uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                failedTypes);

        return new UStruct(schemaKey, fields, typeParameterCount);
    }
}
