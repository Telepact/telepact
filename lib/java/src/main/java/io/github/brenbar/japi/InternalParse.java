package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

class InternalParse {

    static JApiSchema newJApiSchemaWithInternalSchema(String jApiSchemaAsJson) {
        var schema = newJApiSchema(jApiSchemaAsJson);
        var internalSchema = newJApiSchema(InternalJApi.JSON);

        schema.original.putAll(internalSchema.original);
        schema.parsed.putAll(internalSchema.parsed);

        return schema;
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
            throw new JApiSchemaParseError("Document root must be an object");
        }

        return new JApiSchema((Map<String, Object>) (Object) japiSchemaAsParsedJson, parsedDefinitions);
    }

    private static Definition parseDefinition(String definitionKey, Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        var definitionWithDocAsParsedJson = jApiSchemaAsParsedJson.get(definitionKey);
        if (definitionWithDocAsParsedJson == null) {
            throw new JApiSchemaParseError("Could not find definition for %s".formatted(definitionKey));
        }

        var regex = Pattern.compile("^(struct|union|enum|fn|event|info).([a-zA-Z_]+[a-zA-Z0-9_]*)$");
        var matcher = regex.matcher(definitionKey);
        matcher.find();
        var keyword = matcher.group(1);

        var definitionAsParsedJson = definitionWithDocAsParsedJson.get(1);

        var parsedDefinition = switch (keyword) {
            case "fn" ->
                parseFunctionDefinition(definitionAsParsedJson, definitionKey, jApiSchemaAsParsedJson,
                        parsedDefinitions);
            case "struct" ->
                parseStructDefinition(definitionAsParsedJson, definitionKey, jApiSchemaAsParsedJson, parsedDefinitions);
            case "enum" ->
                parseEnumDefinition(definitionAsParsedJson, definitionKey, jApiSchemaAsParsedJson, parsedDefinitions);
            case "info" -> new TitleDefinition(definitionKey);
            default -> throw new JApiSchemaParseError("Unrecognized japi keyword %s".formatted(keyword));
        };

        return parsedDefinition;
    }

    private static FunctionDefinition parseFunctionDefinition(
            Object definitionAsParsedJson,
            String definitionKey,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        List<Object> definitionArray;
        Map<String, Object> inputDefinitionAsParsedJson;
        try {
            definitionArray = (List<Object>) definitionAsParsedJson;
            inputDefinitionAsParsedJson = (Map<String, Object>) definitionArray.get(0);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }
        var inputFields = new HashMap<String, FieldDeclaration>();
        for (var entry : inputDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
            inputFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        Map<String, Object> outputDefinitionAsParsedJson;
        try {
            outputDefinitionAsParsedJson = (Map<String, Object>) definitionArray.get(2);
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        Map<String, Object> outputOkDefinitionAsParsedJson;
        try {
            outputOkDefinitionAsParsedJson = (Map<String, Object>) outputDefinitionAsParsedJson.get("ok");
            outputOkDefinitionAsParsedJson.size();
        } catch (ClassCastException | NullPointerException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        var outputFields = new HashMap<String, FieldDeclaration>();
        for (var entry : outputOkDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
            outputFields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        Map<String, Object> errorEnumAsParsedJson;
        try {
            errorEnumAsParsedJson = (Map<String, Object>) outputDefinitionAsParsedJson.getOrDefault("err",
                    new HashMap<>());
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        var errorValues = new HashMap<String, Struct>();
        {
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
                var struct = new Struct("%s.%s".formatted(definitionKey, enumCase), fields);
                errorValues.put(enumCase, struct);
            }

        }

        var inputStruct = new Struct("%s".formatted(definitionKey), inputFields);
        var outputStruct = new Struct("%s.ok".formatted(definitionKey), outputFields);
        var errorEnum = new Enum("%s.err".formatted(definitionKey), errorValues);

        return new FunctionDefinition(definitionKey, inputStruct, outputStruct, errorEnum);
    }

    private static TypeDefinition parseStructDefinition(
            Object definitionAsParsedJson,
            String definitionKey,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        Map<String, Object> structDefinitionAsParsedJson;
        try {
            structDefinitionAsParsedJson = (Map<String, Object>) definitionAsParsedJson;
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

    private static ErrorDefinition parseErrorDefinition(
            Object definitionAsParsedJson,
            String definitionKey,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        Map<String, Object> errorDefinitionAsParsedJson;
        try {
            errorDefinitionAsParsedJson = (Map<String, Object>) definitionAsParsedJson;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid error definition for %s".formatted(definitionKey));
        }

        var fields = new HashMap<String, FieldDeclaration>();
        for (var entry : errorDefinitionAsParsedJson.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(fieldDeclaration,
                    typeDeclarationValue, false, jApiSchemaAsParsedJson, parsedDefinitions);
            fields.put(parsedField.fieldName, parsedField.fieldDeclaration);
        }

        return new ErrorDefinition(definitionKey, fields);
    }

    private static TypeDefinition parseEnumDefinition(
            Object definitionAsParsedJson,
            String definitionKey,
            Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        Map<String, Object> enumDefinitionAsParsedJson;
        try {
            enumDefinitionAsParsedJson = (Map<String, Object>) definitionAsParsedJson;
        } catch (ClassCastException e) {
            throw new JApiSchemaParseError("Invalid enum definition for %s".formatted(definitionKey));
        }

        var values = new HashMap<String, Struct>();
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
            boolean isForUnion,
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
            throw new JApiSchemaParseError("Type declarations should be strings");
        }

        if (optional && isForUnion) {
            throw new JApiSchemaParseError("Union keys cannot be marked as optional");
        }

        var typeDeclaration = parseType(typeDeclarationString, jApiSchemaAsParsedJson, parsedDefinitions);

        return new FieldNameAndFieldDeclaration(fieldName, new FieldDeclaration(typeDeclaration, optional));
    }

    private static TypeDeclaration parseType(String typeDeclaration, Map<String, List<Object>> jApiSchemaAsParsedJson,
            Map<String, Definition> parsedDefinitions) {
        var regex = Pattern.compile(
                "^((null|boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct)\\.([a-zA-Z_]\\w*)))(\\?)?$");
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
            throw new JApiSchemaParseError("Cannot reference a function in type declarations");
        } else if (definition instanceof ErrorDefinition e) {
            throw new JApiSchemaParseError("Cannot reference an error in type declarations");
        } else {
            throw new JApiSchemaParseError("Unknown definition: %s".formatted(typeDeclaration));
        }
    }
}
