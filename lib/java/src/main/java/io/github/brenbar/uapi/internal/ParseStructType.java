package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;

import static io.github.brenbar.uapi.internal.Append.append;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.AsMap.asMap;
import static io.github.brenbar.uapi.internal.ParseStructFields.parseStructFields;

public class ParseStructType {
    static _UStruct parseStructType(List<Object> path, Map<String, Object> structDefinitionAsPseudoJson,
            String schemaKey, List<String> ignoreKeys, int typeParameterCount, List<Object> uApiSchemaPseudoJson,
            Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var otherKeys = new HashSet<>(structDefinitionAsPseudoJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");
        otherKeys.remove("_ignoreIfDuplicate");
        for (final var ignoreKey : ignoreKeys) {
            otherKeys.remove(ignoreKey);
        }

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = append(path, k);

                parseFailures.add(new _SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        final List<Object> thisPath = append(path, schemaKey);
        final Object defInit = structDefinitionAsPseudoJson.get(schemaKey);

        Map<String, Object> definition = null;
        try {
            definition = asMap(defInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> branchParseFailures = getTypeUnexpectedParseFailure(thisPath,
                    defInit, "Object");

            parseFailures.addAll(branchParseFailures);
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final var fields = parseStructFields(definition, thisPath, typeParameterCount,
                uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                failedTypes);

        return new _UStruct(schemaKey, fields, typeParameterCount);
    }
}
