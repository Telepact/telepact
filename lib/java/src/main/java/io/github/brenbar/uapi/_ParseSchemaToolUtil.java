package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;

class _ParseSchemaToolUtil {

    public static List<_SchemaParseFailure> offsetSchemaIndex(List<_SchemaParseFailure> initialFailures, int offset) {
        final var finalList = new ArrayList<_SchemaParseFailure>();

        for (final var f : initialFailures) {
            final String reason = f.reason;
            final List<Object> path = f.path;
            final Map<String, Object> data = f.data;
            final var newPath = new ArrayList<>(path);

            newPath.set(0, (Integer) newPath.get(0) - offset);

            final Map<String, Object> finalData;
            if (reason.equals("PathCollision")) {
                final var otherNewPath = new ArrayList<>((List<Object>) data.get("other"));

                otherNewPath.set(0, (Integer) otherNewPath.get(0) - offset);
                finalData = Map.of("other", otherNewPath);
            } else {
                finalData = data;
            }

            finalList.add(new _SchemaParseFailure(newPath, reason, finalData));
        }

        return finalList;
    }

    public static String findSchemaKey(Map<String, Object> definition, int index) {
        final var regex = "^((fn|error|info)|((struct|union|_ext)(<[0-2]>)?))\\..*";
        final var matches = new ArrayList<String>();

        for (final var e : definition.keySet()) {
            if (e.matches(regex)) {
                matches.add(e);
            }
        }

        if (matches.size() == 1) {
            return matches.get(0);
        } else {
            throw new UApiSchemaParseError(List.of(new _SchemaParseFailure(List.of(index),
                    "ObjectKeyRegexMatchCountUnexpected",
                    new TreeMap<>(
                            Map.of("regex", regex, "actual", matches.size(), "expected", 1)))));
        }
    }

    public static String findMatchingSchemaKey(Set<String> schemaKeys, String schemaKey) {
        for (final var k : schemaKeys) {
            var splitK = k.split("\\.")[1];
            var splitSchemaKey = schemaKey.split("\\.")[1];
            if (Objects.equals(splitK, splitSchemaKey)) {
                return k;
            }
        }
        return null;
    }

    public static List<_SchemaParseFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
            String expectedType) {
        final var actualType = _Util.getType(value);
        final Map<String, Object> data = new TreeMap<>(Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                Map.entry("expected", Map.of(expectedType, Map.of()))));
        return List.of(
                new _SchemaParseFailure(path, "TypeUnexpected", data));
    }

}
