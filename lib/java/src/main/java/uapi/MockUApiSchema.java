package uapi;

import static uapi.internal.mock.CreateMockUApiSchemaFromJsonDocuments.createMockUApiSchemaFromJsonDocuments;

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
        return createMockUApiSchemaFromJsonDocuments(Map.of("auto_", json));
    }

    public static MockUApiSchema fromJsonDocuments(Map<String, String> jsonDocuments) {
        return createMockUApiSchemaFromJsonDocuments(jsonDocuments);
    }
}
