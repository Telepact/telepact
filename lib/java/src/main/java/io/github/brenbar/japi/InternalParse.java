package io.github.brenbar.japi;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;
import java.util.regex.Pattern;

class InternalParse {

    static JApiSchema newJApiSchemaWithInternalSchema(String jApiSchemaAsJson) {
        var combinedSchemaJson = combineJsonSchemas(List.of(
                jApiSchemaAsJson,
                InternalJApi.getJson()));
        var schema = newJApiSchema(combinedSchemaJson);

        return schema;
    }

    static String combineJsonSchemas(List<String> jsonSchemas) {
        var objectMapper = new ObjectMapper();
        var finalJsonObject = new HashMap<String, Object>();

        try {
            var pseudoJsonSchemas = new ArrayList<Map<String, Object>>();
            for (var jsonSchema : jsonSchemas) {
                var pseudoJsonSchema = objectMapper.readValue(jsonSchema, new TypeReference<Map<String, Object>>() {
                });
                pseudoJsonSchemas.add(pseudoJsonSchema);
            }

            var jsonSchemaKeys = new HashSet<String>();
            var duplicatedJsonSchemaKeys = new HashSet<String>();
            for (var pseudoJsonSchema : pseudoJsonSchemas) {
                var keys = pseudoJsonSchema.keySet();
                for (var key : keys) {
                    if (jsonSchemaKeys.contains(key)) {
                        duplicatedJsonSchemaKeys.add(key);
                    } else {
                        jsonSchemaKeys.add(key);
                    }
                }
            }

            if (!duplicatedJsonSchemaKeys.isEmpty()) {
                var sortedKeys = new TreeSet<String>(duplicatedJsonSchemaKeys);
                throw new JApiSchemaParseError(
                        "Cannot combine schemas due to duplicate keys: %s".formatted(sortedKeys));
            }

            for (var pseudoJsonSchema : pseudoJsonSchemas) {
                finalJsonObject.putAll(pseudoJsonSchema);
            }

            return objectMapper.writeValueAsString(finalJsonObject);
        } catch (JsonProcessingException e) {
            throw new JApiSchemaParseError("Could not combine schemas", e);
        }
    }

    private static JApiSchema newJApiSchema(String jApiSchemaAsJson) {
        var parsedTypes = new HashMap<String, Type>();

        var objectMapper = new ObjectMapper();
        Map<String, Object> japiSchemaAsParsedJson;
        try {
            japiSchemaAsParsedJson = objectMapper.readValue(jApiSchemaAsJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError("Document root must be an object", e);
        }

        var schemaKeys = japiSchemaAsParsedJson.keySet();

        var traitSchemaKeys = new HashSet<String>();

        for (var schemaKey : schemaKeys) {
            if (schemaKey.startsWith("//")) {
                continue;
            }

            if (schemaKey.startsWith("trait.")) {
                traitSchemaKeys.add(schemaKey);
                continue;
            }

            getOrParseType(schemaKey, japiSchemaAsParsedJson, parsedTypes);
        }

        // Apply trait to all functions
        for (var traitSchemaKey : traitSchemaKeys) {

            Map<String, Object> traitDefinition;
            try {
                traitDefinition = (Map<String, Object>) japiSchemaAsParsedJson.get(traitSchemaKey);
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid trait definition %s".formatted(traitSchemaKey));
            }

            var traitArg = (Struct) parseFunctionArgumentType(traitSchemaKey, japiSchemaAsParsedJson, parsedTypes,
                    true);
            var traitResult = (Enum) parseFunctionResultType(traitSchemaKey, japiSchemaAsParsedJson, parsedTypes,
                    true);

            for (var parsedType : parsedTypes.entrySet()) {
                if (parsedType.getKey().matches("^fn\\.[a-zA-Z_]\\w*") && parsedType.getValue() instanceof Struct f) {
                    if (f.name.startsWith("fn._")) {
                        // Only internal traits can change internal functions
                        if (!traitSchemaKey.startsWith("trait._")) {
                            continue;
                        }
                    }

                    for (var traitArgumentField : traitArg.fields.entrySet()) {
                        var newKey = traitArgumentField.getKey();
                        var argField = f.fields.get("arg");
                        if (argField.typeDeclaration.type instanceof Struct s) {
                            if (s.fields.containsKey(newKey)) {
                                throw new JApiSchemaParseError(
                                        "Trait argument field already in use: %s".formatted(newKey));
                            }
                            s.fields.put(newKey, traitArgumentField.getValue());
                        }
                    }

                    for (var traitResultField : traitResult.values.entrySet()) {
                        var newKey = traitResultField.getKey();
                        var resultField = f.fields.get("result");

                        if (resultField.typeDeclaration.type instanceof Enum e) {
                            if (e.values.containsKey(newKey)) {
                                throw new JApiSchemaParseError(
                                        "Trait argument field already in use: %s".formatted(newKey));
                            }
                            e.values.put(newKey, traitResultField.getValue());
                        }
                    }
                }
            }
        }

        // Finish setting up all functions definition
        if (parsedTypes.containsKey("fn.*")) {
            var allFunctionsDefinition = (Enum) parsedTypes.get("fn.*");
            for (var parsedDefinition : parsedTypes.entrySet()) {
                if (parsedDefinition.getKey().startsWith("fn.") && parsedDefinition.getValue() instanceof Struct f
                        && !f.name.startsWith("fn._")) {
                    allFunctionsDefinition.values.put(f.name, f);
                }
            }
        }

        // Finish setting up all functions definition
        if (parsedTypes.containsKey("fn.*.arg")) {
            var allFunctionArgsDefinition = (Enum) parsedTypes.get("fn.*.arg");
            for (var parsedDefinition : parsedTypes.entrySet()) {
                if (parsedDefinition.getKey().endsWith(".arg") && parsedDefinition.getValue() instanceof Struct a
                        && !a.name.startsWith("fn._")) {
                    allFunctionArgsDefinition.values.put(a.name, a);
                }
            }
        }

        return new JApiSchema((Map<String, Object>) (Object) japiSchemaAsParsedJson, parsedTypes);
    }

    private static Type parseFunctionArgumentType(
            String schemaKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes,
            boolean isForTrait) {
        Map<String, Object> definitionObject;
        try {
            definitionObject = (Map<String, Object>) jApiSchemaAsParsedJson.get(schemaKey);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(schemaKey));
        }

        var typeName = "%s.arg".formatted(schemaKey);
        if (isForTrait) {
            if (!definitionObject.containsKey("arg")) {
                return new Struct(typeName, new HashMap<>());
            }
        }

        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) definitionObject.get("arg");
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(schemaKey));
        }
        var argumentFields = new HashMap<String, FieldDeclaration>();
        for (var entry : argumentDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            if (fieldDeclaration.startsWith("//")) {
                continue;
            }
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes);
            argumentFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var type = new Struct(typeName, argumentFields);

        if (!isForTrait) {
            parsedTypes.put(typeName, type);
        }

        return type;
    }

    private static Type parseFunctionResultType(
            String schemaKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes,
            boolean isForTrait) {
        Map<String, Object> definitionObject;
        try {
            definitionObject = (Map<String, Object>) jApiSchemaAsParsedJson.get(schemaKey);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(schemaKey));
        }

        var typeName = "%s.result".formatted(schemaKey);
        if (isForTrait) {
            if (!definitionObject.containsKey("result")) {
                return new Enum(typeName, new HashMap<>());
            }
        }

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) definitionObject.get("result");
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(schemaKey));
        }

        if (!isForTrait && !resultDefinitionAsParsedJson.containsKey("ok")) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(schemaKey));
        }

        var values = new HashMap<String, Struct>();
        for (var entry : resultDefinitionAsParsedJson.entrySet()) {
            Map<String, Object> enumValueData;
            try {
                enumValueData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid function definition for %s".formatted(schemaKey));
            }
            var enumValue = entry.getKey();

            var fields = new HashMap<String, FieldDeclaration>();
            for (var structEntry : enumValueData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                if (fieldDeclaration.startsWith("//")) {
                    continue;
                }
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = parseField(fieldDeclaration,
                        typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new Struct("%s.%s".formatted(schemaKey, enumValue), fields);

            values.put(enumValue, enumStruct);
        }

        var type = new Enum(typeName, values);

        if (!isForTrait) {
            parsedTypes.put(typeName, type);
        }

        return type;
    }

    private static Type parseFunctionType(
            String schemaKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes) {
        var argumentStructType = getOrParseType("%s.arg".formatted(schemaKey), jApiSchemaAsParsedJson,
                parsedTypes);
        var resultEnumType = (Enum) getOrParseType("%s.result".formatted(schemaKey), jApiSchemaAsParsedJson,
                parsedTypes);

        if (!resultEnumType.values.containsKey("ok")) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(schemaKey));
        }

        var fields = Map.ofEntries(
                Map.entry("arg", new FieldDeclaration(new TypeDeclaration(argumentStructType, false), false)),
                Map.entry("result", new FieldDeclaration(new TypeDeclaration(resultEnumType, false), false)));

        var type = new Struct(schemaKey, fields);

        parsedTypes.put(schemaKey, type);

        return type;
    }

    private static Type parseStructType(
            Map<String, Object> structDefinitionAsParsedJson,
            String definitionKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes) {
        var fields = new HashMap<String, FieldDeclaration>();
        for (var entry : structDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            if (fieldDeclaration.startsWith("//")) {
                continue;
            }
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes);
            fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var type = new Struct(definitionKey, fields);

        parsedTypes.put(definitionKey, type);

        return type;
    }

    private static Type parseEnumType(
            Map<String, Object> enumDefinitionAsParsedJson,
            String definitionKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes) {

        var values = new HashMap<String, Struct>();
        for (var entry : enumDefinitionAsParsedJson.entrySet()) {
            if (entry.getKey().startsWith("//")) {
                continue;
            }
            Map<String, Object> enumStructData;
            try {
                enumStructData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid enum definition for %s".formatted(definitionKey));
            }
            var enumValue = entry.getKey();

            var fields = new HashMap<String, FieldDeclaration>();
            for (var structEntry : enumStructData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                if (fieldDeclaration.startsWith("//")) {
                    continue;
                }
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = parseField(fieldDeclaration,
                        typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new Struct("%s.%s".formatted(definitionKey, enumValue), fields);

            values.put(enumValue, enumStruct);
        }

        var type = new Enum(definitionKey, values);

        parsedTypes.put(definitionKey, type);

        return type;
    }

    private static FieldNameAndFieldDeclaration parseField(
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForEnum,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes) {
        var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$");
        var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            throw new JApiSchemaParseError("Could not parse field declaration: %s".formatted(fieldDeclaration));
        }

        String fieldName = matcher.group(1);

        boolean optional = matcher.group(2) != null;

        String typeDeclarationString;
        try {
            typeDeclarationString = (String) typeDeclarationValue;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError(
                    "Type declarations should be strings: %s %s".formatted(fieldDeclaration, typeDeclarationValue));
        }

        if (optional && isForEnum) {
            throw new JApiSchemaParseError("Enum keys cannot be marked as optional");
        }

        var typeDeclaration = parseTypeDeclaration(typeDeclarationString, jApiSchemaAsParsedJson, parsedTypes);

        return new FieldNameAndFieldDeclaration(fieldName, new FieldDeclaration(typeDeclaration, optional));
    }

    private static TypeDeclaration parseTypeDeclaration(String typeDeclaration,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes) {
        var regex = Pattern.compile("^(.*?)(\\?)?$");
        var matcher = regex.matcher(typeDeclaration);
        if (!matcher.find()) {
            throw new JApiSchemaParseError("Could not parse type declaration: %s".formatted(typeDeclaration));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        var type = getOrParseType(typeName, jApiSchemaAsParsedJson, parsedTypes);

        return new TypeDeclaration(type, nullable);
    }

    private static Type getOrParseType(String typeName, Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes) {
        var existingType = parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        var regex = Pattern.compile(
                "^((boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct)\\.([a-zA-Z_]\\w*))|((fn\\.(([a-zA-Z_]\\w*)|(\\*)))(\\.(arg|result))?))$");
        var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new JApiSchemaParseError("Unrecognized type: %s".formatted(typeName));
        }

        var standardTypeName = matcher.group(2);
        if (standardTypeName != null) {
            return switch (standardTypeName) {
                case "boolean" -> new JsonBoolean();
                case "integer" -> new JsonInteger();
                case "number" -> new JsonNumber();
                case "string" -> new JsonString();
                case "any" -> new JsonAny();
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(standardTypeName));
            };
        }

        var collectionTypeName = matcher.group(4);
        if (collectionTypeName != null) {
            var nestedName = matcher.group(6);

            TypeDeclaration nestedType;
            if (nestedName != null) {
                nestedType = parseTypeDeclaration(nestedName, jApiSchemaAsParsedJson, parsedTypes);
            } else {
                nestedType = new TypeDeclaration(new JsonAny(), false);
            }

            return switch (collectionTypeName) {
                case "array" -> new JsonArray(nestedType);
                case "object" -> new JsonObject(nestedType);
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(collectionTypeName));
            };
        }

        var customTypeName = matcher.group(7);
        if (customTypeName != null) {
            var typePrefix = matcher.group(8);
            var typeDefinition = (Map<String, Object>) jApiSchemaAsParsedJson.get(customTypeName);
            return switch (typePrefix) {
                case "struct" ->
                    parseStructType(typeDefinition, customTypeName, jApiSchemaAsParsedJson, parsedTypes);
                case "enum" -> parseEnumType(typeDefinition, typeName, jApiSchemaAsParsedJson, parsedTypes);
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(collectionTypeName));
            };
        }

        var functionTypeName = matcher.group(11);
        if (functionTypeName != null) {
            var isAllFunctions = matcher.group(14);
            var isJustArg = matcher.group(15);

            if (isAllFunctions == null) {
                if (isJustArg == null) {
                    return parseFunctionType(functionTypeName, jApiSchemaAsParsedJson, parsedTypes);
                } else {
                    if (".arg".equals(isJustArg)) {
                        return parseFunctionArgumentType(functionTypeName, jApiSchemaAsParsedJson, parsedTypes, false);
                    } else if (".result".equals(isJustArg)) {
                        return parseFunctionResultType(functionTypeName, jApiSchemaAsParsedJson, parsedTypes, false);
                    }
                }
            } else {
                if (isJustArg == null) {
                    var allFunctionsType = parsedTypes.get(functionTypeName);
                    if (allFunctionsType == null) {
                        allFunctionsType = new Enum(functionTypeName, new HashMap<>());
                        parsedTypes.put(functionTypeName, allFunctionsType);
                    }
                    return allFunctionsType;
                } else {
                    var allFunctionArgsType = parsedTypes.get(functionTypeName);
                    if (allFunctionArgsType == null) {
                        allFunctionArgsType = new Enum(functionTypeName, new HashMap<>());
                        parsedTypes.put(functionTypeName, allFunctionArgsType);
                    }
                    return allFunctionArgsType;
                }
            }
        }

        throw new JApiSchemaParseError("Invalid type: %s".formatted(typeName));
    }
}
