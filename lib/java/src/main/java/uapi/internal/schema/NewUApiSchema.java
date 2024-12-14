package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseUApiSchema.parseUApiSchema;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import uapi.UApiSchema;
import uapi.UApiSchemaParseError;

public class NewUApiSchema {
    public static UApiSchema newUApiSchema(Map<String, List<String>> uApiSchemaJsonDocuments) {
        final var objectMapper = new ObjectMapper();
        final var finalPseudoJson = new HashMap<String, List<Object>>();

        for (var uApiSchemaJson : uApiSchemaJsonDocuments.entrySet()) {
            var documentName = uApiSchemaJson.getKey();

            final Object uApiSchemaPseudoJsonInit;
            try {
                uApiSchemaPseudoJsonInit = objectMapper.readValue(uApiSchemaJson.getValue().get(0),
                        new TypeReference<>() {
                        });
            } catch (IOException e) {
                throw new UApiSchemaParseError(
                        List.of(new SchemaParseFailure(documentName, List.of(), "JsonInvalid", Map.of())),
                        e);
            }

            if (!(uApiSchemaPseudoJsonInit instanceof List)) {
                final List<SchemaParseFailure> thisParseFailure = getTypeUnexpectedParseFailure(documentName, List.of(),
                        uApiSchemaPseudoJsonInit, "Array");
                throw new UApiSchemaParseError(thisParseFailure);
            }
            final List<Object> uApiSchemaPseudoJson = (List<Object>) uApiSchemaPseudoJsonInit;

            finalPseudoJson.put(documentName, uApiSchemaPseudoJson);
        }

        return parseUApiSchema(finalPseudoJson);
    }
}
