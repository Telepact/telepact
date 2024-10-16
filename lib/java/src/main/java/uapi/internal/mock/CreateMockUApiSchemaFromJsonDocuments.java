package uapi.internal.mock;

import static uapi.internal.schema.GetInternalUApiJson.getInternalUApiJson;
import static uapi.internal.schema.NewUApiSchema.newUApiSchema;
import static uapi.internal.schema.ExtendUApiSchema.extendUApiSchema;
import static uapi.internal.schema.GetMockUApiJson.getMockUApiJson;

import java.util.ArrayList;
import java.util.List;

import uapi.UApiSchema;

public class CreateMockUApiSchemaFromJsonDocuments {
    public static UApiSchema createMockUApiSchemaFromJsonDocuments(List<String> jsonDocuments) {
        var finalJsonDocuemnts = new ArrayList<String>();
        finalJsonDocuemnts.addAll(jsonDocuments);
        finalJsonDocuemnts.add(getMockUApiJson());
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
