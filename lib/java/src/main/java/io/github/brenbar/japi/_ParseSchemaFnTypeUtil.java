package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class _ParseSchemaFnTypeUtil {

    static UFn parseFunctionType(
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions,
            boolean isForTrait) {
        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get(schemaKey);
        } catch (ClassCastException e) {
            var index = schemaKeysToIndex.get(schemaKey);
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].%s".formatted(index, schemaKey),
                    "ObjectTypeRequired", Map.of())));
        }
        var argumentFields = new HashMap<String, UFieldDeclaration>();
        var isForUnion = false;
        var typeParameterCount = 0;
        for (var entry : argumentDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = _ParseSchemaCustomTypeUtil.parseField(schemaKey, fieldDeclaration,
                    typeDeclarationValue, isForUnion, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions);
            String fieldName = parsedField.fieldName;
            argumentFields.put(fieldName, parsedField);
        }

        var argType = new UStruct(schemaKey, argumentFields, typeParameterCount);
        var callType = new UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get("->");
        } catch (ClassCastException e) {
            var index = schemaKeysToIndex.get(schemaKey);
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].->".formatted(index),
                    "ObjectTypeRequired", Map.of())));
        }

        if (!isForTrait) {
            if (!resultDefinitionAsParsedJson.containsKey("Ok")) {
                var index = schemaKeysToIndex.get(schemaKey);
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure("[%d].->.Ok".formatted(index),
                        "RequiredKeyMissing", Map.of())));
            }
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();

        var values = new HashMap<String, UStruct>();
        for (var entry : resultDefinitionAsParsedJson.entrySet()) {
            Map<String, Object> unionValueData;
            try {
                unionValueData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                var unionValue = entry.getKey();
                var index = schemaKeysToIndex.get(schemaKey);
                parseFailures.add(new SchemaParseFailure("[%d].->.%s".formatted(index, unionValue),
                        "ObjectTypeRequired", Map.of()));
                continue;
            }
            var unionValue = entry.getKey();

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : unionValueData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = _ParseSchemaCustomTypeUtil.parseField(schemaKey, fieldDeclaration,
                        typeDeclarationValue, isForUnion, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions);
                String fieldName = parsedField.fieldName;
                fields.put(fieldName, parsedField);
            }

            var unionStruct = new UStruct("->.%s".formatted(unionValue), fields, typeParameterCount);

            values.put(unionValue, unionStruct);
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var resultType = new UUnion("%s.->".formatted(schemaKey), values, typeParameterCount);

        var type = new UFn(schemaKey, callType, resultType);

        return type;
    }
}
