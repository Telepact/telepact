package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class UApiSchema {

    final List<Object> original;
    final Map<String, _UType> parsed;
    final Map<String, _UType> typeExtensions;

    public UApiSchema(List<Object> original,
            Map<String, _UType> parsed,
            Map<String, _UType> typeExtensions) {
        this.original = original;
        this.parsed = parsed;
        this.typeExtensions = typeExtensions;
    }

    public static UApiSchema fromJson(String json) {
        return _ParseSchemaUtil.newUApiSchema(json, new HashMap<>());
    }

    public static UApiSchema fromJsonWithExtensions(String json, Map<String, _UType> typeExtensions) {
        return _ParseSchemaUtil.newUApiSchema(json, typeExtensions);
    }

    public static UApiSchema extendWithExtensions(UApiSchema base, String json, Map<String, _UType> typeExtensions) {
        return _ParseSchemaUtil.extendUApiSchema(base, json, typeExtensions);
    }

    public static UApiSchema extend(UApiSchema base, String json) {
        return _ParseSchemaUtil.extendUApiSchema(base, json, new HashMap<>());
    }
}
