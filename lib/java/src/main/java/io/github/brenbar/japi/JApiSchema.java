package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

public class JApiSchema {

    final List<Object> original;
    final Map<String, Type> parsed;

    public JApiSchema(String jApiSchemaJson) {
        var tuple = _ParseUtil.newJApiSchema(jApiSchemaJson, new HashMap<>());
        this.original = tuple.original;
        this.parsed = tuple.parsed;
    }

    public JApiSchema(String jApiSchemaJson, Map<String, TypeExtension> typeExtensions) {
        var tuple = _ParseUtil.newJApiSchema(jApiSchemaJson, typeExtensions);
        this.original = tuple.original;
        this.parsed = tuple.parsed;
    }

    public JApiSchema(JApiSchema first, JApiSchema second) {

        // Any traits in the first schema need to be applied to the second
        for (var e : first.parsed.entrySet()) {
            if (e.getValue() instanceof Trait t) {
                if (second.parsed.containsKey(t.name)) {
                    throw new JApiSchemaParseError(
                            "Could not combine schemas due to duplicate trait %s".formatted(t.name));
                }
                _ParseUtil.applyTraitToParsedTypes(t, second.parsed);
            }
        }

        // And vice versa
        for (var e : second.parsed.entrySet()) {
            if (e.getValue() instanceof Trait t) {
                if (first.parsed.containsKey(t.name)) {
                    throw new JApiSchemaParseError(
                            "Could not combine schemas due to duplicate trait %s".formatted(t.name));
                }
                _ParseUtil.applyTraitToParsedTypes(t, first.parsed);
            }
        }

        // Check for duplicates
        var duplicatedJsonSchemaKeys = new HashSet<String>();
        for (var key : first.parsed.keySet()) {
            if (second.parsed.containsKey(key)) {
                duplicatedJsonSchemaKeys.add(key);
            }
        }
        if (!duplicatedJsonSchemaKeys.isEmpty()) {
            var sortedKeys = new TreeSet<String>(duplicatedJsonSchemaKeys);
            throw new JApiSchemaParseError(
                    "Final schema has duplicate keys: %s".formatted(sortedKeys));
        }

        var original = new ArrayList<Object>();
        original.addAll(first.original);
        original.addAll(second.original);

        var parsed = new HashMap<String, Type>();
        parsed.putAll(first.parsed);
        parsed.putAll(second.parsed);

        this.original = original;
        this.parsed = parsed;
    }
}
