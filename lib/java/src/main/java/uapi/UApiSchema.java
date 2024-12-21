package uapi;

import static uapi.internal.schema.CreateUApiSchemaFromFileJsonMap.createUApiSchemaFromFileJsonMap;
import static uapi.internal.schema.GetSchemaFileMap.getSchemaFileMap;

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
        return createUApiSchemaFromFileJsonMap(Map.of("auto_", json));
    }

    public static UApiSchema fromFileJsonMap(Map<String, String> fileJsonMap) {
        return createUApiSchemaFromFileJsonMap(fileJsonMap);
    }

    public static UApiSchema fromDirectory(String directory) {
        final var map = getSchemaFileMap(directory);
        return createUApiSchemaFromFileJsonMap(map);
    }
}
