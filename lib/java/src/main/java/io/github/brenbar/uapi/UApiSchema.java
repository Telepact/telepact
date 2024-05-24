package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import io.github.brenbar.uapi.internal.types.UFieldDeclaration;
import io.github.brenbar.uapi.internal.types.UType;

import static io.github.brenbar.uapi.internal.ExtendUApiSchema.extendUApiSchema;
import static io.github.brenbar.uapi.internal.NewUApiSchema.newUApiSchema;

/**
 * A parsed uAPI schema.
 */
public class UApiSchema {

    public final List<Object> original;
    public final Map<String, UType> parsed;
    public final Map<String, UFieldDeclaration> parsedRequestHeaders;
    public final Map<String, UFieldDeclaration> parsedResponseHeaders;
    public final Map<String, UType> typeExtensions;

    public UApiSchema(List<Object> original,
            Map<String, UType> parsed,
            Map<String, UFieldDeclaration> parsedRequestHeaders,
            Map<String, UFieldDeclaration> parsedResponseHeaders,
            Map<String, UType> typeExtensions) {
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
