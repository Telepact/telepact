package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.TreeSet;

public class JApiSchema {

    JApiSchemaTuple schemas;

    public JApiSchema(String jApiSchemaJson) {
        this.schemas = InternalParse.newJApiSchema(jApiSchemaJson, new HashMap<>());
    }

    public JApiSchema(String jApiSchemaJson, Map<String, TypeExtension> typeExtensions) {
        this.schemas = InternalParse.newJApiSchema(jApiSchemaJson, typeExtensions);
    }

    public JApiSchema(JApiSchema first, JApiSchema second) {

        // Any traits in the first schema need to be applied to the second
        for (var e : first.schemas.parsed.entrySet()) {
            if (e.getValue() instanceof Trait t) {
                if (second.schemas.parsed.containsKey(t.name)) {
                    throw new JApiSchemaParseError(
                            "Could not combine schemas due to duplicate trait %s".formatted(t.name));
                }
                InternalParse.applyTraitToParsedTypes(t, second.schemas.parsed);
            }
        }

        // And vice versa
        for (var e : second.schemas.parsed.entrySet()) {
            if (e.getValue() instanceof Trait t) {
                if (first.schemas.parsed.containsKey(t.name)) {
                    throw new JApiSchemaParseError(
                            "Could not combine schemas due to duplicate trait %s".formatted(t.name));
                }
                InternalParse.applyTraitToParsedTypes(t, first.schemas.parsed);
            }
        }

        // Check for duplicates
        var duplicatedJsonSchemaKeys = new HashSet<String>();
        for (var key : first.schemas.parsed.keySet()) {
            if (second.schemas.parsed.containsKey(key)) {
                duplicatedJsonSchemaKeys.add(key);
            }
        }
        if (!duplicatedJsonSchemaKeys.isEmpty()) {
            var sortedKeys = new TreeSet<String>(duplicatedJsonSchemaKeys);
            throw new JApiSchemaParseError(
                    "Final schema has duplicate keys: %s".formatted(sortedKeys));
        }

        var original = new ArrayList<Object>();
        original.addAll(first.schemas.original);
        original.addAll(second.schemas.original);

        var parsed = new HashMap<String, Type>();
        parsed.putAll(first.schemas.parsed);
        parsed.putAll(second.schemas.parsed);

        this.schemas = new JApiSchemaTuple(original, parsed);
    }
}
