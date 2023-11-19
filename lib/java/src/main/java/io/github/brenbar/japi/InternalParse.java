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

    static JApiSchema newJApiSchemaWithInternalSchema(String jApiSchemaAsJson,
            Map<String, TypeExtension> typeExtensions) {
        var combinedSchemaJson = combineJsonSchemas(List.of(
                jApiSchemaAsJson,
                InternalJApi.getJson()));
        var schema = newJApiSchema(combinedSchemaJson, typeExtensions);

        return schema;
    }

    static String combineJsonSchemas(List<String> jsonSchemas) {
        var objectMapper = new ObjectMapper();
        var finalJsonList = new ArrayList<Object>();

        var pseudoJsonSchemas = new ArrayList<Object>();
        for (var jsonSchema : jsonSchemas) {
            List<Object> pseudoJsonSchema;
            try {
                pseudoJsonSchema = objectMapper.readValue(jsonSchema, new TypeReference<List<Object>>() {
                });
            } catch (JsonProcessingException e) {
                throw new JApiSchemaParseError("Document root must be an array of objects", e);
            }
            pseudoJsonSchemas.add(pseudoJsonSchema);
        }

        var jsonSchemaKeys = new HashSet<String>();
        var duplicatedJsonSchemaKeys = new HashSet<String>();
        for (var pseudoJsonSchema : pseudoJsonSchemas) {
            var definitions = (List<Object>) pseudoJsonSchema;
            for (var definition : definitions) {
                var definitionAsPsuedoJson = (Map<String, Object>) definition;
                var key = findSchemaKey(definitionAsPsuedoJson);
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
                    "Final schema has duplicate keys: %s".formatted(sortedKeys));
        }

        for (var pseudoJsonSchema : pseudoJsonSchemas) {
            var definitions = (List<Object>) pseudoJsonSchema;
            finalJsonList.addAll(definitions);
        }

        try {
            return objectMapper.writeValueAsString(finalJsonList);
        } catch (JsonProcessingException e) {
            throw new JApiSchemaParseError("Could not combine schemas", e);
        }
    }

    private static String findSchemaKey(Map<String, Object> definition) {
        for (var e : definition.keySet()) {
            if (e.matches("^(struct|enum|fn|trait|info|ext)\\..*")) {
                return e;
            }
        }
        throw new JApiSchemaParseError(
                "Invalid definition. Each definition should have one key matching the regex ^(struct|enum|fn|trait|info|ext)\\..* but was %s"
                        .formatted(definition));
    }

    private static JApiSchema newJApiSchema(String jApiSchemaAsJson, Map<String, TypeExtension> typeExtensions) {
        var parsedTypes = new HashMap<String, Type>();

        var objectMapper = new ObjectMapper();
        List<Map<String, Object>> initialJapiSchemaAsParsedJson;
        try {
            initialJapiSchemaAsParsedJson = objectMapper.readValue(jApiSchemaAsJson, new TypeReference<>() {
            });
        } catch (IOException e) {
            throw new JApiSchemaParseError("Document root must be an array of objects", e);
        }

        var japiSchemaAsParsedJson = new HashMap<String, Object>();

        for (var definition : initialJapiSchemaAsParsedJson) {
            String schemaKey = findSchemaKey(definition);
            japiSchemaAsParsedJson.put(schemaKey, definition);
        }

        var schemaKeys = japiSchemaAsParsedJson.keySet();

        var traitSchemaKeys = new HashSet<String>();

        for (var schemaKey : schemaKeys) {
            if (schemaKey.startsWith("trait.")) {
                traitSchemaKeys.add(schemaKey);
                continue;
            }

            getOrParseType(schemaKey, japiSchemaAsParsedJson, parsedTypes, typeExtensions);
        }

        // Apply trait to all functions
        for (var traitSchemaKey : traitSchemaKeys) {

            var traitDefinition = (Map<String, Object>) japiSchemaAsParsedJson.get(traitSchemaKey);

            Map<String, Object> def;
            try {
                def = (Map<String, Object>) traitDefinition.get(traitSchemaKey);
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid trait definition %s".formatted(traitSchemaKey));
            }

            String traitFunctionRegex;
            String traitFunctionKey;
            if (def.containsKey("fn.*")) {
                traitFunctionKey = "fn.*";
                traitFunctionRegex = "^fn\\.[a-zA-Z]";
            } else if (def.containsKey("fn._?*")) {
                if (!traitSchemaKey.startsWith("trait._")) {
                    throw new JApiSchemaParseError("Invalid trait definition %s".formatted(traitSchemaKey));
                }
                traitFunctionKey = "fn._?*";
                traitFunctionRegex = "^fn\\.[a-zA-Z_]";
            } else {
                throw new JApiSchemaParseError("Invalid trait definition %s".formatted(traitSchemaKey));
            }

            var traitFunction = parseFunctionType(def, traitFunctionKey, japiSchemaAsParsedJson, parsedTypes,
                    typeExtensions,
                    true);

            for (var parsedType : parsedTypes.entrySet()) {
                Fn f;
                try {
                    f = (Fn) parsedType.getValue();
                } catch (ClassCastException e) {
                    continue;
                }

                var regex = Pattern.compile(traitFunctionRegex);
                var matcher = regex.matcher(f.name);
                if (!matcher.find()) {
                    continue;
                }

                if (f.name.startsWith("fn._")) {
                    // Only internal traits can change internal functions
                    if (!traitSchemaKey.startsWith("trait._")) {
                        continue;
                    }
                }

                for (var traitArgumentField : traitFunction.arg.fields.entrySet()) {
                    var newKey = traitArgumentField.getKey();
                    if (f.arg.fields.containsKey(newKey)) {
                        throw new JApiSchemaParseError(
                                "Trait argument field already in use: %s".formatted(newKey));
                    }
                    f.arg.fields.put(newKey, traitArgumentField.getValue());
                }

                for (var traitResultField : traitFunction.result.values.entrySet()) {
                    var newKey = traitResultField.getKey();
                    if (f.result.values.containsKey(newKey)) {
                        throw new JApiSchemaParseError(
                                "Trait argument field already in use: %s".formatted(newKey));
                    }
                    f.result.values.put(newKey, traitResultField.getValue());
                }
            }
        }

        // Ensure all type extensions are defined
        for (var entry : typeExtensions.entrySet()) {
            var typeExtensionName = entry.getKey();
            var typeExtension = (Ext) parsedTypes.get(typeExtensionName);
            if (typeExtension == null) {
                throw new JApiSchemaParseError("Undefined extension %s".formatted(typeExtensionName));
            }
        }

        return new JApiSchema((Map<String, Object>) (Object) japiSchemaAsParsedJson, parsedTypes);
    }

    private static Fn parseFunctionType(
            Map<String, Object> functionDefinitionAsParsedJson,
            String definitionKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes,
            Map<String, TypeExtension> typeExtensions,
            boolean isForTrait) {
        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get(definitionKey);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }
        var argumentFields = new HashMap<String, FieldDeclaration>();
        for (var entry : argumentDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);
            argumentFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var argType = new Struct(definitionKey, argumentFields);

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) functionDefinitionAsParsedJson.get("->");
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        if (!isForTrait) {
            if (!resultDefinitionAsParsedJson.containsKey("ok")) {
                throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
            }
        }

        var values = new HashMap<String, Struct>();
        for (var entry : resultDefinitionAsParsedJson.entrySet()) {
            Map<String, Object> enumValueData;
            try {
                enumValueData = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
            }
            var enumValue = entry.getKey();

            var fields = new HashMap<String, FieldDeclaration>();
            for (var structEntry : enumValueData.entrySet()) {
                var fieldDeclaration = structEntry.getKey();
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = parseField(fieldDeclaration,
                        typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new Struct("->.%s".formatted(enumValue), fields);

            values.put(enumValue, enumStruct);
        }

        var resultType = new Enum("%s.->".formatted(definitionKey), values);

        var type = new Fn(definitionKey, argType, resultType);

        return type;
    }

    private static Struct parseStructType(
            Map<String, Object> structDefinitionAsParsedJson,
            String definitionKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var definition = (Map<String, Object>) structDefinitionAsParsedJson.get(definitionKey);

        var fields = new HashMap<String, FieldDeclaration>();
        for (var entry : definition.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);
            fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var type = new Struct(definitionKey, fields);

        return type;
    }

    private static Enum parseEnumType(
            Map<String, Object> enumDefinitionAsParsedJson,
            String definitionKey,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
        var definition = (Map<String, Object>) enumDefinitionAsParsedJson.get(definitionKey);

        var values = new HashMap<String, Struct>();
        for (var entry : definition.entrySet()) {
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
                var typeDeclarationValue = structEntry.getValue();
                var parsedField = parseField(fieldDeclaration,
                        typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new Struct("%s.%s".formatted(definitionKey, enumValue), fields);

            values.put(enumValue, enumStruct);
        }

        var type = new Enum(definitionKey, values);

        return type;
    }

    private static FieldNameAndFieldDeclaration parseField(
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForEnum,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes,
            Map<String, TypeExtension> typeExtensions) {
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

        var typeDeclaration = parseTypeDeclaration(typeDeclarationString, jApiSchemaAsParsedJson, parsedTypes,
                typeExtensions);

        return new FieldNameAndFieldDeclaration(fieldName, new FieldDeclaration(typeDeclaration, optional));
    }

    private static TypeDeclaration parseTypeDeclaration(String typeDeclaration,
            Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes, Map<String, TypeExtension> typeExtensions) {
        var regex = Pattern.compile("^(.*?)(\\?)?$");
        var matcher = regex.matcher(typeDeclaration);
        if (!matcher.find()) {
            throw new JApiSchemaParseError("Could not parse type declaration: %s".formatted(typeDeclaration));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        var type = getOrParseType(typeName, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);

        return new TypeDeclaration(type, nullable);
    }

    private static Type getOrParseType(String typeName, Map<String, Object> jApiSchemaAsParsedJson,
            Map<String, Type> parsedTypes, Map<String, TypeExtension> typeExtensions) {
        var existingType = parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        var regex = Pattern.compile(
                "^((boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct|fn|info|ext)\\.([a-zA-Z_]\\w*)))$");
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
                nestedType = parseTypeDeclaration(nestedName, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);
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
            var definition = (Map<String, Object>) jApiSchemaAsParsedJson.get(customTypeName);
            var type = switch (typePrefix) {
                case "struct" ->
                    parseStructType(definition, customTypeName, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);
                case "enum" -> parseEnumType(definition, typeName, jApiSchemaAsParsedJson, parsedTypes, typeExtensions);
                case "fn" -> parseFunctionType(definition, customTypeName, jApiSchemaAsParsedJson, parsedTypes,
                        typeExtensions, false);
                case "info" -> new Info(customTypeName);
                case "ext" -> {
                    var typeExtension = typeExtensions.get(customTypeName);
                    if (typeExtension == null) {
                        throw new JApiSchemaParseError("Type extensions must be configured in Server.Options");
                    }
                    yield new Ext(customTypeName, typeExtension);
                }
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(collectionTypeName));
            };

            parsedTypes.put(customTypeName, type);

            return type;
        }

        throw new JApiSchemaParseError("Invalid type: %s".formatted(typeName));
    }
}
