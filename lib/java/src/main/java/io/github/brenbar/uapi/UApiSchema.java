package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal._UFieldDeclaration;
import io.github.brenbar.uapi.internal._UType;

import static io.github.brenbar.uapi.internal.ExtendUApiSchema.extendUApiSchema;
import static io.github.brenbar.uapi.internal.NewUApiSchema.newUApiSchema;

/**
 * A parsed uAPI schema.
 */
public class UApiSchema {

    public final List<Object> original;
    public final Map<String, _UType> parsed;
    public final Map<String, _UFieldDeclaration> parsedRequestHeaders;
    public final Map<String, _UFieldDeclaration> parsedResponseHeaders;
    public final Map<String, _UType> typeExtensions;

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
        return newUApiSchema(json, new HashMap<>());
    }

    public static UApiSchema extend(UApiSchema base, String json) {
        return extendUApiSchema(base, json, new HashMap<>());
    }
}
