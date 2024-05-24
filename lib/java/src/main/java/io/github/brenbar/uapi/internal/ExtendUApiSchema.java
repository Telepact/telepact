package io.github.brenbar.uapi.internal;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import io.github.brenbar.uapi.UApiSchema;
import io.github.brenbar.uapi.UApiSchemaParseError;

import static io.github.brenbar.uapi.internal.AsList.asList;
import static io.github.brenbar.uapi.internal.ParseUApiSchema.parseUApiSchema;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;

public class ExtendUApiSchema {

    public static UApiSchema extendUApiSchema(UApiSchema first, String secondUApiSchemaJson,
            Map<String, UType> secondTypeExtensions) {
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

        final List<Object> secondUApiSchemaPseudoJson;
        try {
            secondUApiSchemaPseudoJson = asList(secondUApiSchemaPseudoJsonInit);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> thisParseFailure = getTypeUnexpectedParseFailure(List.of(),
                    secondUApiSchemaPseudoJsonInit, "Array");
            throw new UApiSchemaParseError(thisParseFailure, e);
        }

        final List<Object> firstOriginal = first.original;
        final Map<String, UType> firstTypeExtensions = first.typeExtensions;

        final var original = new ArrayList<Object>();

        original.addAll(firstOriginal);
        original.addAll(secondUApiSchemaPseudoJson);

        final var typeExtensions = new HashMap<String, UType>();

        typeExtensions.putAll(firstTypeExtensions);
        typeExtensions.putAll(secondTypeExtensions);

        return parseUApiSchema(original, typeExtensions, firstOriginal.size());
    }
}
