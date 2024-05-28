package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseUApiSchema.parseUApiSchema;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import uapi.UApiSchema;
import uapi.UApiSchemaParseError;
import uapi.internal.types.UType;

public class NewUApiSchema {
    public static UApiSchema newUApiSchema(String uApiSchemaJson, Map<String, UType> typeExtensions) {
        final var objectMapper = new ObjectMapper();

        final Object uApiSchemaPseudoJsonInit;
        try {
            uApiSchemaPseudoJsonInit = objectMapper.readValue(uApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new UApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "JsonInvalid", Map.of(), null)),
                    e);
        }

        if (!(uApiSchemaPseudoJsonInit instanceof List)) {
            final List<SchemaParseFailure> thisParseFailure = getTypeUnexpectedParseFailure(List.of(),
                    uApiSchemaPseudoJsonInit, "Array");
            throw new UApiSchemaParseError(thisParseFailure);
        }
        final List<Object> uApiSchemaPseudoJson = (List<Object>) uApiSchemaPseudoJsonInit;

        return parseUApiSchema(uApiSchemaPseudoJson, typeExtensions, 0);
    }
}
