package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

class InternalParse {

    private static TypeDeclaration parseType(Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions, String typeDeclaration) {
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
                default -> throw new JapiParseError("Unrecognized type: %s".formatted(name));
            };

            if (type instanceof JsonNull) {
                if (nullable) {
                    throw new JapiParseError("Cannot declare null type as nullable");
                }
                nullable = true;
            }

            return new TypeDeclaration(type, nullable);
        } catch (Exception e) {
            if (e instanceof JapiParseError e1) {
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
                nestedType = parseType(japiAsJsonJava, parsedDefinitions, nestedName);
            } else {
                nestedType = new TypeDeclaration(new JsonAny(), false);
            }

            var type = switch (name) {
                case "array" -> new JsonArray(nestedType);
                case "object" -> new JsonObject(nestedType);
                default -> throw new JapiParseError("Unrecognized type: %s".formatted(name));
            };

            return new TypeDeclaration(type, nullable);
        } catch (Exception e) {
            if (e instanceof JapiParseError e1) {
                throw e1;
            }
        }

        var name = matcher.group(7);
        if (name == null) {
            throw new JapiParseError("Invalid definition: %s".formatted(typeDeclaration));
        }

        var definition = parsedDefinitions.computeIfAbsent(name,
                (k) -> parseDefinition(japiAsJsonJava, parsedDefinitions, name));
        if (definition instanceof TypeDefinition t) {
            return new TypeDeclaration(t.type(), nullable);
        } else if (definition instanceof FunctionDefinition f) {
            throw new JapiParseError("Cannot reference a function in type declarations");
        } else if (definition instanceof ErrorDefinition e) {
            throw new JapiParseError("Cannot reference an error in type declarations");
        } else {
            throw new JapiParseError("Unknown definition: %s".formatted(typeDeclaration));
        }
    }

    private static FieldNameAndFieldDeclaration parseField(
            Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions,
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForUnion) {
        var regex = Pattern.compile("^([a-zA-Z_]+[a-zA-Z0-9_]*)(!)?$");
        var matcher = regex.matcher(fieldDeclaration);
        matcher.find();

        String fieldName = matcher.group(1);

        boolean optional = matcher.group(2) != null;

        if (optional && isForUnion) {
            throw new JapiParseError("Union keys cannot be marked as optional");
        }

        String typeDeclarationString;
        try {
            typeDeclarationString = (String) typeDeclarationValue;
        } catch (ClassCastException e) {
            throw new JapiParseError("Type declarations should be strings");
        }

        var typeDeclaration = parseType(japiAsJsonJava, parsedDefinitions, typeDeclarationString);

        return new FieldNameAndFieldDeclaration(fieldName, new FieldDeclaration(typeDeclaration, optional));
    }

    private static ErrorDefinition parseErrorDefinition(
            String definitionKey,
            Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions,
            Object definitionAsJsonJava) {
        Map<String, Object> errorDefinitionAsJsonJava;
        try {
            errorDefinitionAsJsonJava = (Map<String, Object>) definitionAsJsonJava;
        } catch (ClassCastException e) {
            throw new JapiParseError("Invalid error definition for %s".formatted(definitionKey));
        }

        var fields = new HashMap<String, FieldDeclaration>();
        for (var entry : errorDefinitionAsJsonJava.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
                    typeDeclarationValue, false);
            fields.put(parsedField.fieldName(), parsedField.fieldDeclaration());
        }

        return new ErrorDefinition(definitionKey, fields);
    }

    private static TypeDefinition parseStructDefinition(
            String definitionKey,
            Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions,
            Object definitionAsJsonJava) {
        Map<String, Object> structDefinitionAsJsonJava;
        try {
            structDefinitionAsJsonJava = (Map<String, Object>) definitionAsJsonJava;
        } catch (ClassCastException e) {
            throw new JapiParseError("Invalid struct definition for %s".formatted(definitionKey));
        }

        var fields = new HashMap<String, FieldDeclaration>();
        for (var entry : structDefinitionAsJsonJava.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
                    typeDeclarationValue, false);
            fields.put(parsedField.fieldName(), parsedField.fieldDeclaration());
        }

        var type = new Struct(definitionKey, fields);

        return new TypeDefinition(definitionKey, type);
    }

    private static TypeDefinition parseEnumDefinition(
            String definitionKey,
            Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions,
            Object definitionAsJsonJava) {
        Map<String, Object> enumDefinitionAsJsonJava;
        try {
            enumDefinitionAsJsonJava = (Map<String, Object>) definitionAsJsonJava;
        } catch (ClassCastException e) {
            throw new JapiParseError("Invalid enum definition for %s".formatted(definitionKey));
        }

        var cases = new HashMap<String, Struct>();
        for (var entry : enumDefinitionAsJsonJava.entrySet()) {
            var enumCase = entry.getKey();
            Map<String, Object> caseStructDefinitionAsJava;
            try {
                caseStructDefinitionAsJava = (Map<String, Object>) entry.getValue();
            } catch (ClassCastException e) {
                throw new JapiParseError("Invalid enum definition for %s".formatted(definitionKey));
            }

            var fields = new HashMap<String, FieldDeclaration>();
            for (var caseStructEntry : caseStructDefinitionAsJava.entrySet()) {
                var caseStructFieldDeclaration = caseStructEntry.getKey();
                var caseStructTypeDeclarationValue = caseStructEntry.getValue();
                var caseStructParsedField = parseField(japiAsJsonJava, parsedDefinitions,
                        caseStructFieldDeclaration, caseStructTypeDeclarationValue, false);
                fields.put(caseStructParsedField.fieldName(), caseStructParsedField.fieldDeclaration());
            }
            var struct = new Struct("%s.%s".formatted(definitionKey, enumCase), fields);
            cases.put(enumCase, struct);
        }

        var type = new Enum(definitionKey, cases);

        return new TypeDefinition(definitionKey, type);
    }

    private static FunctionDefinition parseFunctionDefinition(
            String definitionKey,
            Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions,
            Object definitionAsJsonJava) {
        List<Object> definitionArray;
        Map<String, Object> inputDefinitionAsJsonJava;
        try {
            definitionArray = (List<Object>) definitionAsJsonJava;
            inputDefinitionAsJsonJava = (Map<String, Object>) definitionArray.get(0);
        } catch (ClassCastException e) {
            throw new JapiParseError("Invalid function definition for %s".formatted(definitionKey));
        }
        var inputFields = new HashMap<String, FieldDeclaration>();
        for (var entry : inputDefinitionAsJsonJava.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
                    typeDeclarationValue, false);
            inputFields.put(parsedField.fieldName(), parsedField.fieldDeclaration());
        }

        Map<String, Object> outputDefinitionAsJsonJava;
        try {
            outputDefinitionAsJsonJava = (Map<String, Object>) definitionArray.get(2);
        } catch (ClassCastException e) {
            throw new JapiParseError("Invalid function definition for %s".formatted(definitionKey));
        }

        var outputFields = new HashMap<String, FieldDeclaration>();
        for (var entry : outputDefinitionAsJsonJava.entrySet()) {
            var fieldDeclaration = entry.getKey();
            var typeDeclarationValue = entry.getValue();
            var parsedField = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
                    typeDeclarationValue, false);
            outputFields.put(parsedField.fieldName(), parsedField.fieldDeclaration());
        }

        List<String> errors = List.of();
        if (definitionArray.size() == 4) {
            var errorDefinition = definitionArray.get(3);

            try {
                errors = (List<String>) errorDefinition;
            } catch (ClassCastException e) {
                throw new JapiParseError("Invalid function definition for %s".formatted(definitionKey));
            }

            for (var errorDef : errors) {
                if (!japiAsJsonJava.containsKey(errorDef)) {
                    throw new JapiParseError("Unknown error reference for %s".formatted(errorDef));
                }
            }
        }

        var inputStruct = new Struct("%s.input", inputFields);
        var outputStruct = new Struct("%s.output", outputFields);

        return new FunctionDefinition(definitionKey, inputStruct, outputStruct, errors);
    }

    private static Definition parseDefinition(Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions, String definitionKey) {
        var definitionAsJsonJavaWithDoc = japiAsJsonJava.get(definitionKey);
        if (definitionAsJsonJavaWithDoc == null) {
            throw new JapiParseError("Could not find definition for %s".formatted(definitionKey));
        }

        var regex = Pattern.compile("^(struct|union|enum|error|function|event|info).([a-zA-Z_]+[a-zA-Z0-9_]*)$");
        var matcher = regex.matcher(definitionKey);
        matcher.find();
        var keyword = matcher.group(1);

        var definitionAsJsonJava = definitionAsJsonJavaWithDoc.get(1);

        var parsedDefinition = switch (keyword) {
            case "function" ->
                parseFunctionDefinition(definitionKey, japiAsJsonJava, parsedDefinitions, definitionAsJsonJava);
            case "struct" ->
                parseStructDefinition(definitionKey, japiAsJsonJava, parsedDefinitions, definitionAsJsonJava);
            case "error" ->
                parseErrorDefinition(definitionKey, japiAsJsonJava, parsedDefinitions, definitionAsJsonJava);
            case "enum" -> parseEnumDefinition(definitionKey, japiAsJsonJava, parsedDefinitions, definitionAsJsonJava);
            case "info" -> new TitleDefinition(definitionKey);
            default -> throw new JapiParseError("Unrecognized japi keyword %s".formatted(keyword));
        };

        return parsedDefinition;
    }

    static Japi newJapi(String japiAsJson) {
        var parsedDefinitions = new HashMap<String, Definition>();

        var objectMapper = new ObjectMapper();
        Map<String, List<Object>> japiAsJsonJava;
        try {
            japiAsJsonJava = objectMapper.readValue(japiAsJson, new TypeReference<>() {
            });

            for (var entry : japiAsJsonJava.entrySet()) {
                var definitionKey = entry.getKey();
                if (!parsedDefinitions.containsKey(definitionKey)) {
                    var definition = parseDefinition(japiAsJsonJava, parsedDefinitions, definitionKey);
                    parsedDefinitions.put(definitionKey, definition);
                }
            }
        } catch (IOException e) {
            throw new JapiParseError("Document root must be an object");
        }

        return new Japi((Map<String, Object>) (Object) japiAsJsonJava, parsedDefinitions);
    }
}
