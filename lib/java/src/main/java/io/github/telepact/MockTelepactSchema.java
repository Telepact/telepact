package io.github.telepact;

import static io.github.telepact.internal.schema.CreateMockTelepactSchemaFromJsonDocuments.createMockTelepactSchemaFromFileJsonMap;
import static io.github.telepact.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.List;
import java.util.Map;

import io.github.telepact.internal.types.VFieldDeclaration;
import io.github.telepact.internal.types.VType;

/**
 * A parsed telepact schema.
 */
public class MockTelepactSchema {

    public final List<Object> original;
    public final Map<String, VType> parsed;
    public final Map<String, VFieldDeclaration> parsedRequestHeaders;
    public final Map<String, VFieldDeclaration> parsedResponseHeaders;

    public MockTelepactSchema(List<Object> original,
            Map<String, VType> parsed,
            Map<String, VFieldDeclaration> parsedRequestHeaders,
            Map<String, VFieldDeclaration> parsedResponseHeaders) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    public static MockTelepactSchema fromJson(String json) {
        return createMockTelepactSchemaFromFileJsonMap(Map.of("auto_", json));
    }

    public static MockTelepactSchema fromFileJsonMap(Map<String, String> fileJsonMap) {
        return createMockTelepactSchemaFromFileJsonMap(fileJsonMap);
    }

    public static MockTelepactSchema fromDirectory(String directory) {
        final var map = getSchemaFileMap(directory);
        return createMockTelepactSchemaFromFileJsonMap(map);
    }
}
