package io.github.msgpact.internal.schema;

import static io.github.msgpact.internal.schema.GetAuthMsgPactJson.getAuthMsgPactJson;
import static io.github.msgpact.internal.schema.GetInternalMsgPactJson.getInternalMsgPactJson;
import static io.github.msgpact.internal.schema.ParseMsgPactSchema.parseMsgPactSchema;

import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

import io.github.msgpact.MsgPactSchema;

public class CreateMsgPactSchemaFromFileJsonMap {
    public static MsgPactSchema createMsgPactSchemaFromFileJsonMap(Map<String, String> jsonDocuments) {
        var finalJsonDocuments = new HashMap<String, String>();
        finalJsonDocuments.putAll(jsonDocuments);
        finalJsonDocuments.put("internal_", getInternalMsgPactJson());

        // Determine if we need to add the auth schema
        for (var json : jsonDocuments.values()) {
            var regex = Pattern.compile("\"struct\\.Auth_\"\\s*:");
            var matcher = regex.matcher(json);
            if (matcher.find()) {
                finalJsonDocuments.put("auth_", getAuthMsgPactJson());
                break;
            }
        }

        var msgPactSchema = parseMsgPactSchema(finalJsonDocuments);

        return msgPactSchema;
    }
}
