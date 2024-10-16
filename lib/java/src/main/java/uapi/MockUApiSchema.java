package uapi;

import static uapi.internal.mock.CreateMockUApiSchemaFromJsonDocuments.createMockUApiSchemaFromJsonDocuments;

import java.util.List;

/**
 * A parsed uAPI schema.
 */
public class MockUApiSchema {

    public final UApiSchema uApiSchema;

    public MockUApiSchema(UApiSchema uApiSchema) {
        this.uApiSchema = uApiSchema;
    }

    public static MockUApiSchema fromJson(String json) {
        var uApiSchema = createMockUApiSchemaFromJsonDocuments(List.of(json));
        return new MockUApiSchema(uApiSchema);
    }

    public static MockUApiSchema fromJsonDocuments(List<String> jsonDocuments) {
        var uApiSchema = createMockUApiSchemaFromJsonDocuments(jsonDocuments);
        return new MockUApiSchema(uApiSchema);
    }
}
