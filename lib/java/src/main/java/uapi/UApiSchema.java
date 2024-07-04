package uapi;

import static uapi.internal.schema.ExtendUApiSchema.extendUApiSchema;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;

/**
 * A parsed uAPI schema.
 */
public class UApiSchema {

    public final List<Object> original;
    public final Map<String, UType> parsed;
    public final Map<String, UFieldDeclaration> parsedRequestHeaders;
    public final Map<String, UFieldDeclaration> parsedResponseHeaders;

    public UApiSchema(List<Object> original,
            Map<String, UType> parsed,
            Map<String, UFieldDeclaration> parsedRequestHeaders,
            Map<String, UFieldDeclaration> parsedResponseHeaders) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    public static UApiSchema fromJson(String json) {
        return newUApiSchema(json);
    }

    public static UApiSchema extend(UApiSchema base, String json) {
        return extendUApiSchema(base, json);
    }
}
