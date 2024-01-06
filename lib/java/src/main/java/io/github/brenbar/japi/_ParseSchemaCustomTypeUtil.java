package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class _ParseSchemaCustomTypeUtil {

    static UStruct parseStructType(
            Map<String, Object> structDefinitionAsParsedJson,
            String schemaKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var definition = (Map<String, Object>) structDefinitionAsParsedJson.get(schemaKey);

        var fields = new HashMap<String, UFieldDeclaration>();
        for (var entry : definition.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(schemaKey, fieldDeclaration,
                    typeDeclarationValue, false, typeParameterCount, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                    typeExtensions);
            String fieldName = parsedField.fieldName;
            fields.put(fieldName, parsedField);
        }

        var type = new UStruct(schemaKey, fields, typeParameterCount);

        return type;
    }

    static UUnion parseUnionType(
            Map<String, Object> unionDefinitionAsParsedJson,
            String schemaKey,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var index = schemaKeysToIndex.get(schemaKey);

        var definition = (Map<String, Object>) unionDefinitionAsParsedJson.get(schemaKey);

        var parseFailures = new ArrayList<SchemaParseFailure>();

        var values = new HashMap<String, UStruct>();
        for (var entry : definition.entrySet()) {
            Map<String, Object> unionStructData;
            try {
                unionStructData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                var unionValue = entry.getKey();
                parseFailures.add(
                        new SchemaParseFailure("[%d].->.%s".formatted(index, unionValue),
                                "ObjectTypeRequired", Map.of()));
                continue;
            }
            var unionValue = entry.getKey();

            var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)$");
            var matcher = regex.matcher(unionValue);
            if (!matcher.find()) {
                parseFailures.add(new SchemaParseFailure("[%d].->".formatted(index),
                        "InvalidUnionValue", Map.of("value", unionValue)));
                continue;
            }

            var fields = new HashMap<String, UFieldDeclaration>();
            for (var structEntry : unionStructData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                UFieldDeclaration parsedField;
                try {
                    parsedField = parseField("[%d].->.%s".formatted(index, unionValue), fieldDeclaration,
                            typeDeclarationValue, false, typeParameterCount, originalJApiSchema, schemaKeysToIndex,
                            parsedTypes,
                            typeExtensions);
                } catch (JApiSchemaParseError e) {
                    parseFailures.addAll(e.schemaParseFailures);
                    continue;
                }
                String fieldName = parsedField.fieldName;
                fields.put(fieldName, parsedField);
            }

            var unionStruct = new UStruct("%s.%s".formatted(schemaKey, unionValue), fields, typeParameterCount);

            values.put(unionValue, unionStruct);
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new UUnion(schemaKey, values, typeParameterCount);

        return type;
    }

    static UFieldDeclaration parseField(
            String path,
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForUnion,
            int typeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$");
        var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "InvalidFieldKey", Map.of("field", fieldDeclaration))));
        }

        String fieldName = matcher.group(1);

        boolean optional = matcher.group(2) != null;

        List<Object> typeDeclarationArray;
        try {
            typeDeclarationArray = (List<Object>) typeDeclarationValue;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayTypeRequired", Map.of())));
        }

        if (optional && isForUnion) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "UnionKeysCannotBeMarkedAsOptional", Map.of())));
        }

        var typeDeclaration = _ParseSchemaTypeUtil.parseTypeDeclaration(path, typeDeclarationArray, typeParameterCount,
                originalJApiSchema,
                schemaKeysToIndex,
                parsedTypes,
                typeExtensions);

        return new UFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
