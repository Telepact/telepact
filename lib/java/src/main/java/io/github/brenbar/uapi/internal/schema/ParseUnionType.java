package io.github.brenbar.uapi.internal.schema;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UFieldDeclaration;
import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UType;
import io.github.brenbar.uapi.internal.types.UUnion;

import static io.github.brenbar.uapi.internal.Append.append;
import static io.github.brenbar.uapi.internal.UnionEntry.unionEntry;
import static io.github.brenbar.uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.schema.ParseStructFields.parseStructFields;

public class ParseUnionType {
    static UUnion parseUnionType(List<Object> path, Map<String, Object> unionDefinitionAsPseudoJson, String schemaKey,
            List<String> ignoreKeys, List<String> requiredKeys, int typeParameterCount,
            List<Object> uApiSchemaPseudoJson,
            Map<String, Integer> schemaKeysToIndex, Map<String, UType> parsedTypes,
            Map<String, UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();

        final var otherKeys = new HashSet<>(unionDefinitionAsPseudoJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");
        for (final var ignoreKey : ignoreKeys) {
            otherKeys.remove(ignoreKey);
        }

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = append(path, k);

                parseFailures.add(new SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of(), null));
            }
        }

        final List<Object> thisPath = append(path, schemaKey);
        final Object defInit = unionDefinitionAsPseudoJson.get(schemaKey);

        if (!(defInit instanceof List)) {
            final List<SchemaParseFailure> finalParseFailures = getTypeUnexpectedParseFailure(thisPath,
                    defInit, "Array");

            parseFailures.addAll(finalParseFailures);
            throw new UApiSchemaParseError(parseFailures);
        }
        final List<Object> definition2 = (List<Object>) defInit;

        final List<Map<String, Object>> definition = new ArrayList<>();
        int index = -1;
        for (final var element : definition2) {
            index += 1;
            final List<Object> loopPath = append(thisPath, index);

            if (!(element instanceof Map)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(loopPath,
                        element, "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            definition.add((Map<String, Object>) element);
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        if (definition.isEmpty() && requiredKeys.isEmpty()) {
            parseFailures.add(new SchemaParseFailure(thisPath, "EmptyArrayDisallowed", Map.of(), null));
        } else {
            outerLoop: for (final var requiredKey : requiredKeys) {
                for (final var element : definition) {
                    final var map = (Map<String, Object>) element;
                    final var keys = new HashSet<>(map.keySet());
                    keys.remove("///");
                    if (keys.contains(requiredKey)) {
                        continue outerLoop;
                    }
                }
                final List<Object> branchPath = append(append(thisPath, 0), requiredKey);
                parseFailures.add(new SchemaParseFailure(branchPath, "RequiredObjectKeyMissing", Map.of(), null));
            }
        }

        final var cases = new HashMap<String, UStruct>();
        final var caseIndices = new HashMap<String, Integer>();

        for (int i = 0; i < definition.size(); i++) {
            final var element = definition.get(i);
            final List<Object> loopPath = append(thisPath, i);

            final var mapInit = (Map<String, Object>) element;
            final var map = new HashMap<>(mapInit);
            map.remove("///");
            final var keys = new ArrayList<>(map.keySet());

            final var regexString = "^([A-Z][a-zA-Z0-9_]*)$";

            final var matches = keys.stream().filter(k -> k.matches(regexString)).toList();
            if (matches.size() != 1) {
                parseFailures.add(
                        new SchemaParseFailure(loopPath,
                                "ObjectKeyRegexMatchCountUnexpected",
                                Map.of("regex", regexString, "actual",
                                        matches.size(), "expected", 1, "keys", keys),
                                null));
                continue;
            }
            if (map.size() != 1) {
                parseFailures.add(new SchemaParseFailure(loopPath, "ObjectSizeUnexpected",
                        Map.of("expected", 1, "actual", map.size()), null));
                continue;
            }

            final var entry = unionEntry(map);
            final var unionCase = entry.getKey();
            final List<Object> unionKeyPath = append(loopPath, unionCase);

            if (!(entry.getValue() instanceof Map)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(unionKeyPath,
                        entry.getValue(), "Object");

                parseFailures.addAll(thisParseFailures);
                continue;
            }
            final Map<String, Object> unionCaseStruct = (Map<String, Object>) entry.getValue();

            final Map<String, UFieldDeclaration> fields;
            try {
                fields = parseStructFields(unionCaseStruct, unionKeyPath, typeParameterCount,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
                continue;
            }

            final var unionStruct = new UStruct("%s.%s".formatted(schemaKey, unionCase), fields, typeParameterCount);

            cases.put(unionCase, unionStruct);
            caseIndices.put(unionCase, i);
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new UUnion(schemaKey, cases, caseIndices, typeParameterCount);
    }
}
