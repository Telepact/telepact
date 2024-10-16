package uapi.internal.schema;

import static uapi.internal.schema.GetInternalUApiJson.getInternalUApiJson;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;
import static uapi.internal.schema.ExtendUApiSchema.extendUApiSchema;

import java.util.ArrayList;
import java.util.List;

import uapi.UApiSchema;

public class CreateUApiSchemaFromJsonDocuments {
    public static UApiSchema createUApiSchemaFromJsonDocuments(List<String> jsonDocuments) {
        var finalJsonDocuemnts = new ArrayList<String>();
        finalJsonDocuemnts.addAll(jsonDocuments);
        finalJsonDocuemnts.add(getInternalUApiJson());

        var initialJsonDocument = finalJsonDocuemnts.get(0);

        var uapiSchema = newUApiSchema(initialJsonDocument);

        var extendedJsonDocuments = finalJsonDocuemnts.subList(1, finalJsonDocuemnts.size());

        for (var jsonDocument : extendedJsonDocuments) {
            uapiSchema = extendUApiSchema(uapiSchema, jsonDocument);
        }

        return uapiSchema;
    }
}
