package uapi.internal.schema;

import static uapi.internal.schema.GetInternalUApiJson.getInternalUApiJson;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;

import java.util.HashMap;
import java.util.Map;

import uapi.UApiSchema;

public class CreateUApiSchemaFromJsonDocuments {
    public static UApiSchema createUApiSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal", getInternalUApiJson());

        var uapiSchema = newUApiSchema(finalJsonDocuments);

        return uapiSchema;
    }
}
