package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class JApiSchema {

    final List<Object> original;
    final Map<String, UType> parsed;
    final Map<String, TypeExtension> typeExtensions;

    public JApiSchema(String jApiSchemaJson) {
        var tuple = _UApiSchemaUtil.parseUApiSchema(jApiSchemaJson, new HashMap<>());
        this.original = tuple.original;
        this.parsed = tuple.parsed;
        this.typeExtensions = tuple.typeExtensions;
    }

    public JApiSchema(String jApiSchemaJson, Map<String, TypeExtension> typeExtensions) {
        var tuple = _UApiSchemaUtil.parseUApiSchema(jApiSchemaJson, typeExtensions);
        this.original = tuple.original;
        this.parsed = tuple.parsed;
        this.typeExtensions = tuple.typeExtensions;
    }

    public JApiSchema(JApiSchema first, JApiSchema second) {
        var tuple = _UApiSchemaUtil.combineUApiSchemas(first, second);
        this.original = tuple.original;
        this.parsed = tuple.parsed;
        this.typeExtensions = tuple.typeExtensions;
    }
}
