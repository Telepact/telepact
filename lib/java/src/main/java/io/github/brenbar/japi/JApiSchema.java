package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class JApiSchema {

    final List<Object> original;
    final Map<String, UType> parsed;
    final Map<String, TypeExtension> typeExtensions;

    public JApiSchema(List<Object> original,
            Map<String, UType> parsed,
            Map<String, TypeExtension> typeExtensions) {
        this.original = original;
        this.parsed = parsed;
        this.typeExtensions = typeExtensions;
    }

    public static JApiSchema fromJson(String json) {
        return _ParseSchemaUtil.newUApiSchema(json, new HashMap<>());
    }

    public static JApiSchema fromJsonWithExtensions(String json, Map<String, TypeExtension> typeExtensions) {
        return _ParseSchemaUtil.newUApiSchema(json, typeExtensions);
    }

    public static JApiSchema extend(JApiSchema base, String json, Map<String, TypeExtension> typeExtensions) {
        return _ParseSchemaUtil.extendUApiSchema(base, json, typeExtensions);
    }

    public static JApiSchema extend(JApiSchema base, String json) {
        return _ParseSchemaUtil.extendUApiSchema(base, json, new HashMap<>());
    }
}
