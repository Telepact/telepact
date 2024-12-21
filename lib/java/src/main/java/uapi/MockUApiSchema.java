package uapi;

import static uapi.internal.schema.CreateMockUApiSchemaFromJsonDocuments.createMockUApiSchemaFromFileJsonMap;
import static uapi.internal.schema.GetSchemaFileMap.getSchemaFileMap;

import java.util.List;
import java.util.Map;

import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;

/**
 * A parsed uAPI schema.
 */
public class MockUApiSchema {

    public final List<Object> original;
    public final Map<String, UType> parsed;
    public final Map<String, UFieldDeclaration> parsedRequestHeaders;
    public final Map<String, UFieldDeclaration> parsedResponseHeaders;

    public MockUApiSchema(List<Object> original,
            Map<String, UType> parsed,
            Map<String, UFieldDeclaration> parsedRequestHeaders,
            Map<String, UFieldDeclaration> parsedResponseHeaders) {
        this.original = original;
        this.parsed = parsed;
        this.parsedRequestHeaders = parsedRequestHeaders;
        this.parsedResponseHeaders = parsedResponseHeaders;
    }

    public static MockUApiSchema fromJson(String json) {
        return createMockUApiSchemaFromFileJsonMap(Map.of("auto_", json));
    }

    public static MockUApiSchema fromFileJsonMap(Map<String, String> fileJsonMap) {
        return createMockUApiSchemaFromFileJsonMap(fileJsonMap);
    }

    public static MockUApiSchema fromDirectory(String directory) {
        final var map = getSchemaFileMap(directory);
        return createMockUApiSchemaFromFileJsonMap(map);
    }
}
