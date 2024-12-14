package uapi.internal.schema;

import static uapi.internal.schema.GetInternalUApiJson.getInternalUApiJson;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import uapi.UApiSchema;

public class CreateUApiSchemaFromJsonDocuments {
    public static UApiSchema createUApiSchemaFromJsonDocuments(Map<String, List<String>> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, List<String>>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal", List.of(getInternalUApiJson()));

        var uapiSchema = newUApiSchema(finalJsonDocuments);

        return uapiSchema;
    }
}
