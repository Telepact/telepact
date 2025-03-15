package io.github.msgpact.internal.schema;

import static io.github.msgpact.internal.schema.CreateMsgPactSchemaFromFileJsonMap.createMsgPactSchemaFromFileJsonMap;
import static io.github.msgpact.internal.schema.GetMockMsgPactJson.getMockMsgPactJson;

import java.util.HashMap;
import java.util.Map;

import io.github.msgpact.MockMsgPactSchema;

public class CreateMockMsgPactSchemaFromJsonDocuments {
    public static MockMsgPactSchema createMockMsgPactSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("mock_", getMockMsgPactJson());

        var msgPactSchema = createMsgPactSchemaFromFileJsonMap(finalJsonDocuments);

        return new MockMsgPactSchema(msgPactSchema.original, msgPactSchema.parsed, msgPactSchema.parsedRequestHeaders,
                msgPactSchema.parsedResponseHeaders);
    }
}
