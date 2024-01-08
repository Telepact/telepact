package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

class _ParseSchemaFnTypeUtil {

    private static final _ParseSchemaFnTypeUtil INST = new _ParseSchemaFnTypeUtil();

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

        var def = functionDefinitionAsParsedJson.get(schemaKey);

        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) def;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(_ParseSchemaUtil.getTypeUnexpectedValidationFailure(fnPath, def, "Object"));
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

        Object resDefInit = functionDefinitionAsParsedJson.get("->");

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) resDefInit;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(resPath, resDefInit, "Object"));
        }

        if (!isForTrait) {
            if (!resultDefinitionAsParsedJson.containsKey("Ok")) {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(_ValidateUtil.append(resPath, "Ok"),
                        "RequiredObjectKeyMissing", Map.of())));
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
                parseFailures.addAll(
                        _ParseSchemaUtil.getTypeUnexpectedValidationFailure(loopPath, entry.getValue(), "Object"));
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
