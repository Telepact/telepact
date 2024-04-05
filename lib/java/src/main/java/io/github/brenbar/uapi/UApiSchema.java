package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * A parsed uAPI schema.
 */
public class UApiSchema {

    final List<Object> original;
    final Map<String, _UType> parsed;
    final Map<String, _UFieldDeclaration> parsedRequestHeaders;
    final Map<String, _UFieldDeclaration> parsedResponseHeaders;
    final Map<String, _UType> typeExtensions;

    public UApiSchema(List<Object> original,
            Map<String, _UType> parsed,
            Map<String, _UFieldDeclaration> parsedRequestHeaders,
            Map<String, _UFieldDeclaration> parsedResponseHeaders,
            Map<String, _UType> typeExtensions) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
        this.typeExtensions = typeExtensions;
    }

    public static UApiSchema fromJson(String json) {
        return _Util.newUApiSchema(json, new HashMap<>());
    }

    public static UApiSchema extend(UApiSchema base, String json) {
        return _Util.extendUApiSchema(base, json, new HashMap<>());
    }
}
