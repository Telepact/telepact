package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseUApiSchema.parseUApiSchema;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import uapi.UApiSchema;
import uapi.UApiSchemaParseError;

public class ExtendUApiSchema {

    public static UApiSchema extendUApiSchema(UApiSchema first, String secondUApiSchemaJson) {
        final var objectMapper = new ObjectMapper();

        final Object secondUApiSchemaPseudoJsonInit;
        try {
            secondUApiSchemaPseudoJsonInit = objectMapper.readValue(secondUApiSchemaJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new UApiSchemaParseError(
                    List.of(new SchemaParseFailure(List.of(), "JsonInvalid", Map.of(), null)),
                    e);
        }

        if (!(secondUApiSchemaPseudoJsonInit instanceof List)) {
            final List<SchemaParseFailure> thisParseFailure = getTypeUnexpectedParseFailure(List.of(),
                    secondUApiSchemaPseudoJsonInit, "Array");
            throw new UApiSchemaParseError(thisParseFailure);
        }
        final List<Object> secondUApiSchemaPseudoJson = (List<Object>) secondUApiSchemaPseudoJsonInit;

        final List<Object> firstOriginal = first.original;

        final var original = new ArrayList<Object>();

        original.addAll(firstOriginal);
        original.addAll(secondUApiSchemaPseudoJson);

        return parseUApiSchema(original, firstOriginal.size());
    }
}
