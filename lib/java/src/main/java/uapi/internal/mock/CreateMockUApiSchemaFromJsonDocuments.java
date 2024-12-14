package uapi.internal.mock;

import static uapi.internal.schema.GetInternalUApiJson.getInternalUApiJson;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;
import static uapi.internal.schema.GetMockUApiJson.getMockUApiJson;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.MockUApiSchema;
import uapi.UApiSchema;

public class CreateMockUApiSchemaFromJsonDocuments {
    public static MockUApiSchema createMockUApiSchemaFromJsonDocuments(Map<String, List<String>> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, List<String>>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal", List.of(getInternalUApiJson()));
        finalJsonDocuments.put("mock", List.of(getMockUApiJson()));

        var uapiSchema = newUApiSchema(finalJsonDocuments);

        return new MockUApiSchema(uapiSchema);
    }
}
