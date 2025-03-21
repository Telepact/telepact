package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.CreateTelepactSchemaFromFileJsonMap.createTelepactSchemaFromFileJsonMap;
import static io.github.telepact.internal.schema.GetMockTelepactJson.getMockTelepactJson;

import java.util.HashMap;
import java.util.Map;

import io.github.telepact.MockTelepactSchema;

public class CreateMockTelepactSchemaFromJsonDocuments {
    public static MockTelepactSchema createMockTelepactSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("mock_", getMockTelepactJson());

        var telepactSchema = createTelepactSchemaFromFileJsonMap(finalJsonDocuments);

        return new MockTelepactSchema(telepactSchema.original, telepactSchema.parsed, telepactSchema.parsedRequestHeaders,
                telepactSchema.parsedResponseHeaders);
    }
}
