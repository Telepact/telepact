package io.github.brenbar.uapi.internal;

import java.io.IOException;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.uapi.UApiSchema;
import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UType;

import static io.github.brenbar.uapi.internal.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.ParseUApiSchema.parseUApiSchema;
import static io.github.brenbar.uapi.internal.AsList.asList;

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

        final List<Object> uApiSchemaPseudoJson;
        try {
            uApiSchemaPseudoJson = asList(uApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(List.of(),
                    uApiSchemaPseudoJsonInit, "Array");
            throw new UApiSchemaParseError(thisParseFailures, e);
        }

        return parseUApiSchema(uApiSchemaPseudoJson, typeExtensions, 0);
    }
}
