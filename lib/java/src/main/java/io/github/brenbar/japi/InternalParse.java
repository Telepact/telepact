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
        var parsedDefinitions = new HashMap<String, Definition>();

        var objectMapper = new ObjectMapper();
        Map<String, List<Object>> japiSchemaAsParsedJson;
        try {
            japiSchemaAsParsedJson = objectMapper.readValue(jApiSchemaAsJson, new TypeReference<>() {
            });

            for (var entry : japiSchemaAsParsedJson.entrySet()) {
                var definitionKey = entry.getKey();
                if (!parsedDefinitions.containsKey(definitionKey)) {
                    var definition = parseDefinition(definitionKey, japiSchemaAsParsedJson, parsedDefinitions);
                    parsedDefinitions.put(definitionKey, definition);
                }
            }
        } catch (IOException e) {
            throw new JApiSchemaParseError("Document root must be an object", e);
        }

        var traits = new ArrayList<FunctionDefinition>();
        for (var def : parsedDefinitions.entrySet()) {
            if (def.getValue() instanceof FunctionDefinition f && def.getKey().startsWith("trait.")) {
                traits.add(f);
            }
        }

        // Apply trait to all functions
        for (var traitDefinition : traits) {

            for (var parsedDefinition : parsedDefinitions.entrySet()) {
                if (parsedDefinition.getValue() instanceof FunctionDefinition f && f.name.startsWith("fn.")) {
                    if (f.name.startsWith("fn._")) {
                        // Only internal traits can change internal functions
                        if (!traitDefinition.name.startsWith("trait._")) {
                            continue;
                        }
                    }

                    for (var traitArgumentField : traitDefinition.argumentStruct.fields.entrySet()) {
                        var newKey = traitArgumentField.getKey();
                        if (f.argumentStruct.fields.containsKey(newKey)) {
                            throw new JApiSchemaParseError(
                                    "Trait argument field already in use: %s".formatted(newKey));
                        }
                        f.argumentStruct.fields.put(newKey, traitArgumentField.getValue());
                    }

                    for (var traitResultField : traitDefinition.resultEnum.values.entrySet()) {
                        var newKey = traitResultField.getKey();
                        if (f.resultEnum.values.containsKey(newKey)) {
                            throw new JApiSchemaParseError(
                                    "Trait argument field already in use: %s".formatted(newKey));
                        }
                        f.resultEnum.values.put(newKey, traitResultField.getValue());
                    }
                }
            }
        }

        // Finish setting up all functions definition
        if (parsedDefinitions.containsKey("fn")) {
            var allFunctionsDefinition = (AllFunctionsDefinition) parsedDefinitions.get("fn");
            for (var parsedDefinition : parsedDefinitions.entrySet()) {
                if (parsedDefinition.getValue() instanceof FunctionDefinition f && f.name.startsWith("fn.")) {
                    allFunctionsDefinition.functions.values.put(f.name, f.argumentStruct);
                }
            }

        }

        return new JApiSchema((Map<String, Object>) (Object) japiSchemaAsParsedJson, parsedDefinitions);
    }

    private static Definition parseDefinition(String definitionKey, Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        if ("fn".equals(definitionKey)) {
            return new AllFunctionsDefinition();
        }

        var definitionWithDocAsParsedJson = jApiSchemaAsParsedJson.get(definitionKey);
        if (definitionWithDocAsParsedJson == null) {
            throw new JApiSchemaParseError("Could not find definition for %s".formatted(definitionKey));
        }

        var regex = Pattern.compile("^(struct|enum|fn|trait|info).([a-zA-Z_]+[a-zA-Z0-9_]*)$");
        var matcher = regex.matcher(definitionKey);
        if (!matcher.find()) {
            throw new JApiSchemaParseError("Invalid type definition name: %s".formatted(definitionKey));
        }
        var keyword = matcher.group(1);

        var parsedDefinition = switch (keyword) {
            case "fn" ->
                parseFunctionDefinition(definitionWithDocAsParsedJson, definitionKey, jApiSchemaAsParsedJson,
                        parsedDefinitions);
            case "trait" ->
                parseFunctionDefinition(definitionWithDocAsParsedJson, definitionKey, jApiSchemaAsParsedJson,
                        parsedDefinitions);
            case "struct" ->
                parseStructDefinition(definitionWithDocAsParsedJson, definitionKey, jApiSchemaAsParsedJson,
                        parsedDefinitions);
            case "enum" ->
                parseEnumDefinition(definitionWithDocAsParsedJson, definitionKey, jApiSchemaAsParsedJson,
                        parsedDefinitions);
            case "info" -> new TitleDefinition(definitionKey);
            default -> throw new JApiSchemaParseError("Unrecognized japi keyword %s".formatted(keyword));
        };

        return parsedDefinition;
    }

    private static FunctionDefinition parseFunctionDefinition(
            List<Object> definitionArray,
            String definitionKey,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        Map<String, Object> argumentDefinitionAsParsedJson;
        try {
            argumentDefinitionAsParsedJson = (Map<String, Object>) definitionArray.get(0);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }
        var argumentFields = new HashMap<String, FieldDeclaration>();
        for (var entry : argumentDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
            argumentFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        Map<String, Object> resultDefinitionAsParsedJson;
        try {
            resultDefinitionAsParsedJson = (Map<String, Object>) definitionArray.get(2);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
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
                        typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new Struct("%s.%s".formatted(definitionKey, enumValue), fields);

            values.put(enumValue, enumStruct);
        }

        var argumentStruct = new Struct(definitionKey, argumentFields);
        var resultEnum = new Enum(definitionKey, values);

        return new FunctionDefinition(definitionKey, argumentStruct, resultEnum);
    }

    private static TypeDefinition parseStructDefinition(
            List<Object> definitionArray,
            String definitionKey,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        Map<String, Object> structDefinitionAsParsedJson;
        try {
            structDefinitionAsParsedJson = (Map<String, Object>) definitionArray.get(0);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid struct definition for %s".formatted(definitionKey));
        }

        var fields = new HashMap<String, FieldDeclaration>();
        for (var entry : structDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
            fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        var type = new Struct(definitionKey, fields);

        return new TypeDefinition(definitionKey, type);
    }

    private static TypeDefinition parseEnumDefinition(
            List<Object> definitionArray,
            String definitionKey,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        Map<String, Object> enumDefinitionAsParsedJson;
        try {
            enumDefinitionAsParsedJson = (Map<String, Object>) definitionArray.get(0);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid enum definition for %s".formatted(definitionKey));
        }

        var values = new HashMap<String, Struct>();
        for (var entry : enumDefinitionAsParsedJson.entrySet()) {
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
                        typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
                fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
            }

            var enumStruct = new Struct("%s.%s".formatted(definitionKey, enumValue), fields);

            values.put(enumValue, enumStruct);
        }

        var type = new Enum(definitionKey, values);

        return new TypeDefinition(definitionKey, type);
    }

    private static FieldNameAndFieldDeclaration parseField(
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForEnum,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$");
        var matcher = regex.matcher(fieldDeclaration);
        matcher.find();

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

        var typeDeclaration = parseType(typeDeclarationString, jApiSchemaAsParsedJson, parsedDefinitions);

        return new FieldNameAndFieldDeclaration(fieldName, new FieldDeclaration(typeDeclaration, optional));
    }

    private static TypeDeclaration parseType(String typeDeclaration, Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        var regex = Pattern.compile(
                "^((boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|(fn)|((enum|struct|fn)\\.([a-zA-Z_]\\w*))|)(\\?)?$");
        var matcher = regex.matcher(typeDeclaration);
        matcher.find();

        boolean nullable = matcher.group(11) != null;

        var standardTypeName = matcher.group(2);
        if (standardTypeName != null) {
            var type = switch (standardTypeName) {
                case "boolean" -> new JsonBoolean();
                case "integer" -> new JsonInteger();
                case "number" -> new JsonNumber();
                case "string" -> new JsonString();
                case "any" -> new JsonAny();
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(standardTypeName));
            };

            return new TypeDeclaration(type, nullable);
        }

        var collectionTypeName = matcher.group(4);
        if (collectionTypeName != null) {
            var nestedName = matcher.group(6);

            TypeDeclaration nestedType;
            if (nestedName != null) {
                nestedType = parseType(nestedName, jApiSchemaAsParsedJson, parsedDefinitions);
            } else {
                nestedType = new TypeDeclaration(new JsonAny(), false);
            }

            var type = switch (collectionTypeName) {
                case "array" -> new JsonArray(nestedType);
                case "object" -> new JsonObject(nestedType);
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(collectionTypeName));
            };

            return new TypeDeclaration(type, nullable);
        }

        var functionRef = matcher.group(7);
        if (functionRef != null) {
            var definition = (AllFunctionsDefinition) parsedDefinitions.get("fn");
            if (definition == null) {
                definition = (AllFunctionsDefinition) parseDefinition("fn", jApiSchemaAsParsedJson, parsedDefinitions);
                parsedDefinitions.put("fn", definition);
            }
            return new TypeDeclaration(definition.functions, nullable);
        }

        var customTypeName = matcher.group(8);
        if (customTypeName != null) {
            var definition = parsedDefinitions.get(customTypeName);
            if (definition == null) {
                definition = parseDefinition(customTypeName, jApiSchemaAsParsedJson, parsedDefinitions);
                parsedDefinitions.put(customTypeName, definition);
            }
            if (definition instanceof TypeDefinition t) {
                return new TypeDeclaration(t.type, nullable);
            } else if (definition instanceof FunctionDefinition f) {
                return new TypeDeclaration(f.argumentStruct, nullable);
            } else {
                throw new JApiSchemaParseError("Unknown definition: %s".formatted(typeDeclaration));
            }
        }

        throw new JApiSchemaParseError("Invalid definition: %s".formatted(typeDeclaration));
    }
}
