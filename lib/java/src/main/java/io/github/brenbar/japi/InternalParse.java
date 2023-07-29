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
                InternalJApi.JSON));
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

                    var traitOkStruct = (Struct) traitDefinition.resultEnum.values.get("ok");
                    var okStruct = (Struct) f.resultEnum.values.get("ok");
                    for (var traitOkStructEntry : traitOkStruct.fields.entrySet()) {
                        var newKey = traitOkStructEntry.getKey();
                        if (okStruct.fields.containsKey(newKey)) {
                            throw new JApiSchemaParseError(
                                    "Trait ok struct field already in use: %s".formatted(newKey));
                        }

                        okStruct.fields.put(newKey, traitOkStructEntry.getValue());
                    }

                    var traitErrEnum = (Map<String, Struct>) traitDefinition.resultEnum.values
                            .get("err");
                    var errEnum = (Map<String, Struct>) f.resultEnum.values.get("err");
                    for (var traitErrStructEntry : traitErrEnum.entrySet()) {
                        var newEnumValue = traitErrStructEntry.getKey();
                        if (errEnum.containsKey(newEnumValue)) {
                            throw new JApiSchemaParseError(
                                    "Trait err enum value (%s) already in use for (%s)".formatted(newEnumValue,
                                            f.name));
                        }

                        errEnum.put(newEnumValue, traitErrStructEntry.getValue());
                    }
                }
            }
        }

        return new JApiSchema((Map<String, Object>) (Object) japiSchemaAsParsedJson, parsedDefinitions);
    }

    private static Definition parseDefinition(String definitionKey, Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
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

        Map<String, Object> resultOkDefinitionAsParsedJson;
        try {
            resultOkDefinitionAsParsedJson = (Map<String, Object>) resultDefinitionAsParsedJson.get("ok");
            resultOkDefinitionAsParsedJson.size();
        } catch (ClassCastException | NullPointerException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        var okStructFields = new HashMap<String, FieldDeclaration>();
        for (var entry : resultOkDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
            okStructFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        Map<String, Object> errorEnumAsParsedJson;
        try {
            errorEnumAsParsedJson = (Map<String, Object>) resultDefinitionAsParsedJson.getOrDefault("err",
                    new HashMap<>());
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        var errorValues = new HashMap<String, Struct>();
        for (var entry : errorEnumAsParsedJson.entrySet()) {
            var enumCase = entry.getKey();
            Map<String, Object> enumStructDefinitionAsParsedJson;
            try {
                enumStructDefinitionAsParsedJson = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid enum definition for %s".formatted(definitionKey));
            }

            var fields = new HashMap<String, FieldDeclaration>();
            for (var enumStructEntry : enumStructDefinitionAsParsedJson.entrySet()) {
                var enumStructFieldDeclaration = enumStructEntry.getKey();
                var enumStructTypeDeclarationValue = enumStructEntry.getValue();
                var enumStructParsedField = parseField(
                        enumStructFieldDeclaration, enumStructTypeDeclarationValue, false, jApiSchemaAsParsedJson,
                        parsedDefinitions);
                fields.put(enumStructParsedField.fieldName, enumStructParsedField.fieldDeclaration);
            }
            var errorValueStruct = new Struct("%s.%s".formatted(definitionKey, enumCase), fields);
            errorValues.put(enumCase, errorValueStruct);
        }

        var argumentStruct = new Struct("%s".formatted(definitionKey), argumentFields);
        var okStruct = new Struct("%s.ok".formatted(definitionKey), okStructFields);

        var resultEnumValues = Map.of("ok", okStruct, "err", errorValues);
        var resultEnum = new Enum(definitionKey, resultEnumValues);

        // TODO: Ensure that `_unknown` is defined.

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

        var values = new HashMap<String, Object>();
        for (var entry : enumDefinitionAsParsedJson.entrySet()) {
            var enumCase = entry.getKey();
            Map<String, Object> enumStructDefinitionAsParsedJson;
            try {
                enumStructDefinitionAsParsedJson = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JApiSchemaParseError("Invalid enum definition for %s".formatted(definitionKey));
            }

            var fields = new HashMap<String, FieldDeclaration>();
            for (var enumStructEntry : enumStructDefinitionAsParsedJson.entrySet()) {
                var enumStructFieldDeclaration = enumStructEntry.getKey();
                var enumStructTypeDeclarationValue = enumStructEntry.getValue();
                var enumStructParsedField = parseField(
                        enumStructFieldDeclaration, enumStructTypeDeclarationValue, false, jApiSchemaAsParsedJson,
                        parsedDefinitions);
                fields.put(enumStructParsedField.fieldName, enumStructParsedField.fieldDeclaration);
            }
            var struct = new Struct("%s.%s".formatted(definitionKey, enumCase), fields);
            values.put(enumCase, struct);
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
                "^((null|boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct|fn)\\.([a-zA-Z_]\\w*)))(\\?)?$");
        var matcher = regex.matcher(typeDeclaration);
        matcher.find();

        boolean nullable = matcher.group(10) != null;

        try {
            var name = matcher.group(2);
            if (name == null) {
                throw new RuntimeException("Ignore: will try another type");
            }
            var type = switch (name) {
                case "null" -> new JsonNull();
                case "boolean" -> new JsonBoolean();
                case "integer" -> new JsonInteger();
                case "number" -> new JsonNumber();
                case "string" -> new JsonString();
                case "any" -> new JsonAny();
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(name));
            };

            if (type instanceof JsonNull) {
                if (nullable) {
                    throw new JApiSchemaParseError("Cannot declare null type as nullable");
                }
                nullable = true;
            }

            return new TypeDeclaration(type, nullable);
        } catch (Exception e) {
            if (e instanceof JApiSchemaParseError e1) {
                throw e1;
            }
        }

        try {
            var name = matcher.group(4);
            if (name == null) {
                throw new RuntimeException("Ignore: will try another type");
            }

            var nestedName = matcher.group(6);

            TypeDeclaration nestedType;
            if (nestedName != null) {
                nestedType = parseType(nestedName, jApiSchemaAsParsedJson, parsedDefinitions);
            } else {
                nestedType = new TypeDeclaration(new JsonAny(), false);
            }

            var type = switch (name) {
                case "array" -> new JsonArray(nestedType);
                case "object" -> new JsonObject(nestedType);
                default -> throw new JApiSchemaParseError("Unrecognized type: %s".formatted(name));
            };

            return new TypeDeclaration(type, nullable);
        } catch (Exception e) {
            if (e instanceof JApiSchemaParseError e1) {
                throw e1;
            }
        }

        var name = matcher.group(7);
        if (name == null) {
            throw new JApiSchemaParseError("Invalid definition: %s".formatted(typeDeclaration));
        }

        var definition = parsedDefinitions.computeIfAbsent(name,
                (k) -> parseDefinition(name, jApiSchemaAsParsedJson, parsedDefinitions));
        if (definition instanceof TypeDefinition t) {
            return new TypeDeclaration(t.type, nullable);
        } else if (definition instanceof FunctionDefinition f) {
            return new TypeDeclaration(f.argumentStruct, nullable);
        } else if (definition instanceof ErrorDefinition e) {
            throw new JApiSchemaParseError("Cannot reference an error in type declarations");
        } else {
            throw new JApiSchemaParseError("Unknown definition: %s".formatted(typeDeclaration));
        }
    }
}
