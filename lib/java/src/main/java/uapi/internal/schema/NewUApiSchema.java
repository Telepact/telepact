package uapi.internal.schema;

import static uapi.internal.schema.ParseUApiSchema.parseUApiSchema;

import java.util.Map;
import uapi.UApiSchema;

public class NewUApiSchema {
    public static UApiSchema newUApiSchema(Map<String, String> uApiSchemaJsonDocuments) {

        return parseUApiSchema(uApiSchemaJsonDocuments);
    }
}
