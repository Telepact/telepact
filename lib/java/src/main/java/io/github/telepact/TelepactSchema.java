package io.github.telepact;

import static io.github.telepact.internal.schema.CreateTelepactSchemaFromFileJsonMap.createTelepactSchemaFromFileJsonMap;
import static io.github.telepact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VFieldDeclaration;
import io.github.telepact.internal.types.VType;

/**
 * A parsed telepact schema.
 */
public class TelepactSchema {

    public final List<Object> original;
    public final Map<String, VType> parsed;
    public final Map<String, VFieldDeclaration> parsedRequestHeaders;
    public final Map<String, VFieldDeclaration> parsedResponseHeaders;

    public TelepactSchema(List<Object> original,
            Map<String, VType> parsed,
            Map<String, VFieldDeclaration> parsedRequestHeaders,
            Map<String, VFieldDeclaration> parsedResponseHeaders) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    public static TelepactSchema fromJson(String json) {
        return createTelepactSchemaFromFileJsonMap(Map.of("auto_", json));
    }

    public static TelepactSchema fromFileJsonMap(Map<String, String> fileJsonMap) {
        return createTelepactSchemaFromFileJsonMap(fileJsonMap);
    }

    public static TelepactSchema fromDirectory(String directory) {
        final var map = getSchemaFileMap(directory);
        return createTelepactSchemaFromFileJsonMap(map);
    }
}
