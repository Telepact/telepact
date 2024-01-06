package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class _ParseSchemaFnTypeUtil {

    static UFn parseFunctionType(
            List<Object> path,
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions,
            boolean isForTrait, List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        var parseFailures = new ArrayList<SchemaParseFailure>();

        var fnPath = _ValidateUtil.append(path, schemaKey);

        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get(schemaKey);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(fnPath,
                    "ObjectTypeRequired", Map.of())));
        }
        var argumentFields = new HashMap<String, UFieldDeclaration>();
        var isForUnion = false;
        var typeParameterCount = 0;
        for (var entry : argumentDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            try {
                var parsedField = _ParseSchemaCustomTypeUtil.parseField(fnPath, fieldDeclaration,
                        typeDeclarationValue, isForUnion, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                        parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
                String fieldName = parsedField.fieldName;
                argumentFields.put(fieldName, parsedField);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        var argType = new UStruct(schemaKey, argumentFields, typeParameterCount);
        var callType = new UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);

        var resPath = _ValidateUtil.append(path, "->");

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get("->");
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(resPath,
                    "ObjectTypeRequired", Map.of())));
        }

        if (!isForTrait) {
            if (!resultDefinitionAsParsedJson.containsKey("Ok")) {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(_ValidateUtil.append(resPath, "Ok"),
                        "RequiredKeyMissing", Map.of())));
            }
        }

        var values = new HashMap<String, UStruct>();
        for (var entry : resultDefinitionAsParsedJson.entrySet()) {
            var unionValue = entry.getKey();
            var loopPath = _ValidateUtil.append(resPath, unionValue);

            Map<String, Object> unionValueData;
            try {
                unionValueData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                parseFailures.add(new SchemaParseFailure(loopPath,
                        "ObjectTypeRequired", Map.of()));
                continue;
            }

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : unionValueData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                try {
                    var parsedField = _ParseSchemaCustomTypeUtil.parseField(loopPath, fieldDeclaration,
                            typeDeclarationValue, isForUnion, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                            parsedTypes,
                            typeExtensions, allParseFailures, failedTypes);
                    String fieldName = parsedField.fieldName;
                    fields.put(fieldName, parsedField);
                } catch (JApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                }
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
