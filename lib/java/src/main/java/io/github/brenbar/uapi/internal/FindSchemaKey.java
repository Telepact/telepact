package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import io.github.brenbar.uapi.UApiSchemaParseError;

public class FindSchemaKey {

    public static String findSchemaKey(Map<String, Object> definition, int index) {
        final var regex = "^(errors|((fn|requestHeader|responseHeader|info)|((struct|union|_ext)(<[0-2]>)?))\\..*)";
        final var matches = new ArrayList<String>();

        final var keys = definition.keySet().stream().sorted().toList();

        for (final var e : keys) {
            if (e.matches(regex)) {
                matches.add(e);
            }
        }

        if (matches.size() == 1) {
            return matches.get(0);
        } else {
            final var parseFailure = new SchemaParseFailure(List.of(index),
                    "ObjectKeyRegexMatchCountUnexpected",
                    new TreeMap<>(
                            Map.of("regex", regex, "actual", matches.size(), "expected", 1, "keys", keys)),
                    null);
            throw new UApiSchemaParseError(List.of(parseFailure));
        }
    }
}
