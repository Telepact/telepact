package uapi.internal.schema;

import static uapi.internal.schema.GetInternalUApiJson.getInternalUApiJson;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;
import static uapi.internal.schema.GetAuthUApiJson.getAuthUApiJson;

import java.util.HashMap;
import java.util.Map;

import uapi.UApiSchema;

public class CreateUApiSchemaFromFileJsonMap {
    public static UApiSchema createUApiSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal_", getInternalUApiJson());

        // Determine if we need to add the auth schema
        for (var json : jsonDocuments.values()) {

            if (json.matches("\"struct\\.Auth_\"[\\s]*")) {
                finalJsonDocuments.put("auth_", getAuthUApiJson());
                break;
            }
        }

        var uApiSchema = newUApiSchema(finalJsonDocuments);

        return uApiSchema;
    }
}
