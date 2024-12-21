package uapi.internal.schema;

import static uapi.internal.schema.GetMockUApiJson.getMockUApiJson;
import static uapi.internal.schema.CreateUApiSchemaFromFileJsonMap.createUApiSchemaFromFileJsonMap;

import java.util.HashMap;
import java.util.Map;

import uapi.MockUApiSchema;

public class CreateMockUApiSchemaFromJsonDocuments {
    public static MockUApiSchema createMockUApiSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("mock_", getMockUApiJson());

        var uApiSchema = createUApiSchemaFromFileJsonMap(finalJsonDocuments);

        return new MockUApiSchema(uApiSchema.original, uApiSchema.parsed, uApiSchema.parsedRequestHeaders,
                uApiSchema.parsedResponseHeaders);
    }
}
