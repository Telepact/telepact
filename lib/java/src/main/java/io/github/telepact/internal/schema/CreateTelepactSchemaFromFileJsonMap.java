package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.GetAuthTelepactJson.getAuthTelepactJson;
import static io.github.telepact.internal.schema.GetInternalTelepactJson.getInternalTelepactJson;
import static io.github.telepact.internal.schema.ParseTelepactSchema.parseTelepactSchema;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchema;

public class CreateTelepactSchemaFromFileJsonMap {
    public static TelepactSchema createTelepactSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal_", getInternalTelepactJson());

        // Determine if we need to add the auth schema
        for (var json : jsonDocuments.values()) {
            var regex = Pattern.compile("\"struct\\.Auth_\"\\s*:");
            var matcher = regex.matcher(json);
            if (matcher.find()) {
                finalJsonDocuments.put("auth_", getAuthTelepactJson());
                break;
            }
        }

        var telepactSchema = parseTelepactSchema(finalJsonDocuments);

        return telepactSchema;
    }
}
