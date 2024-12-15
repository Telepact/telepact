package uapi.internal.mock;

import static uapi.internal.schema.GetInternalUApiJson.getInternalUApiJson;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;
import static uapi.internal.schema.GetMockUApiJson.getMockUApiJson;

import java.util.HashMap;
import java.util.Map;

import uapi.MockUApiSchema;

public class CreateMockUApiSchemaFromJsonDocuments {
    public static MockUApiSchema createMockUApiSchemaFromJsonDocuments(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal", getInternalUApiJson());
        finalJsonDocuments.put("mock", getMockUApiJson());

        var uapiSchema = newUApiSchema(finalJsonDocuments);

        return new MockUApiSchema(uapiSchema.original, uapiSchema.parsed, uapiSchema.parsedRequestHeaders,
                uapiSchema.parsedResponseHeaders);
    }
}
