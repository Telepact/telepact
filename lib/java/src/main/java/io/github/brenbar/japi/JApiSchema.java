package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class JApiSchema {

    final List<Object> original;
    final Map<String, Type> parsed;

    public JApiSchema(String jApiSchemaJson) {
        var tuple = _JApiSchemaUtil.parseJApiSchema(jApiSchemaJson, new HashMap<>());
        this.original = tuple.original;
        this.parsed = tuple.parsed;
    }

    public JApiSchema(String jApiSchemaJson, Map<String, TypeExtension> typeExtensions) {
        var tuple = _JApiSchemaUtil.parseJApiSchema(jApiSchemaJson, typeExtensions);
        this.original = tuple.original;
        this.parsed = tuple.parsed;
    }

    public JApiSchema(JApiSchema first, JApiSchema second) {
        var tuple = _JApiSchemaUtil.combineJApiSchemas(first, second);
        this.original = tuple.original;
        this.parsed = tuple.parsed;
    }
}
