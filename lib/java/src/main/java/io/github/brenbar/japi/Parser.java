package io.github.brenbar.japi;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class Parser {

    public interface Type {
        public String getName();
    }

    public static class JsonNull implements Type {
        @Override
        public String getName() {
            return "null";
        }
    }
    public static class JsonBoolean implements Type {
        @Override
        public String getName() {
            return "boolean";
        }
    }
    public static class JsonInteger implements Type {
        @Override
        public String getName() {
            return "integer";
        }
    }
    public static class JsonNumber implements Type {
        @Override
        public String getName() {
            return "number";
        }
    }
    public static class JsonString implements Type {
        @Override
        public String getName() {
            return "string";
        }
    }
    public record JsonArray(TypeDeclaration nestedType) implements Type {
        @Override
        public String getName() {
            return "array";
        }
    }
    public record JsonObject(TypeDeclaration nestedType) implements Type {
        @Override
        public String getName() {
            return "object";
        }
    }
    public record Struct(String name, Map<String, FieldDeclaration> fields) implements Type {
        @Override
        public String getName() {
            return name;
        }
    }
    public record Enum(String name, Map<String, FieldDeclaration> cases) implements Type {
        @Override
        public String getName() {
            return name;
        }
    }
    public static class JsonAny implements Type {
        @Override
        public String getName() {
            return "any";
        }
    }


    public record TypeDeclaration(
        Type type,
        boolean nullable
    ) {}

    public interface Definition {
        public String getName();
    }

    public record FieldDeclaration(
        TypeDeclaration typeDeclaration,
        boolean optional
    ) {}

    public record FunctionDefinition(
            String name,
            Struct inputStruct,
            Struct outputStruct,
            List<String> errors
    ) implements Definition {
        @Override
        public String getName() {
            return name;
        }
    }

    public record TypeDefinition(
        String name,
        Type type
    ) implements Definition {
        @Override
        public String getName() {
            return name;
        }
    }

    public record ErrorDefinition(
            String name,
            Map<String, FieldDeclaration> fields
    ) implements Definition {
        @Override
        public String getName() {
            return name;
        }
    }

    public record TitleDefinition(
            String name
    ) implements Definition {
        @Override
        public String getName() {
            return name;
        }
    }

    private record FieldNameAndFieldDeclaration(
            String fieldName,
            FieldDeclaration fieldDeclaration
    ) {}

    public static class JapiParseError extends RuntimeException {
        public JapiParseError(String message) {
            super(message);
        }
    }

    public record Japi(Map<String, Object> original, Map<String, Definition> parsed) {}

    public static Japi newJapi(String japiAsJson) {
        var parsedDefinitions = new HashMap<String, Definition>();

        var objectMapper = new ObjectMapper();
        Map<String, List<Object>> japiAsJsonJava;
        try {
            japiAsJsonJava = objectMapper.readValue(japiAsJson, new TypeReference<>(){});

            for (var entry : japiAsJsonJava.entrySet()) {
                var definitionKey = entry.getKey();
                if (!parsedDefinitions.containsValue(definitionKey)) {
                    var definition = parseDefinition(japiAsJsonJava, parsedDefinitions, definitionKey);
                    parsedDefinitions.put(definitionKey, definition);
                }
            }
        } catch (IOException e) {
            throw new JapiParseError("Document root must be an object");
        }

        return new Japi((Map<String, Object>) (Object) japiAsJsonJava, parsedDefinitions);
    }

    private static Definition parseDefinition(Map<String, List<Object>> japiAsJsonJava, Map<String, Definition> parsedDefinitions, String definitionKey) {
        var definitionAsJsonJava = japiAsJsonJava.get(definitionKey);
        if (definitionAsJsonJava == null) {
            throw new JapiParseError("Could not find definition for %s".formatted(definitionKey));
        }

        var splitName = splitDefinitionKeywordAndName(definitionKey);
        var keyword = splitName.get(0);
        var definitionName = splitName.get(1);

        var definitionArray = definitionAsJsonJava.stream().filter(l -> !(l instanceof String)).collect(Collectors.toList());

        var parsedDefinition = switch (keyword) {
            case "function" -> {
                if (definitionArray.size() < 2) {
                    throw new JapiParseError("Invalid function definition");
                }

                Map<String, Object> inputDefinitionAsJsonJava;
                try {
                    inputDefinitionAsJsonJava = (Map<String, Object>) definitionArray.get(0);
                } catch (ClassCastException e) {
                    throw new JapiParseError("Invalid function definition");
                }
                var inputFields = new HashMap<String, FieldDeclaration>();
                for (var entry : inputDefinitionAsJsonJava.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration, typeDeclarationValue, false);
                    inputFields.put(result.fieldName, result.fieldDeclaration);
                }

                Map<String, Object> outputDefinitionAsJsonJava;
                try {
                    outputDefinitionAsJsonJava = (Map<String, Object>) definitionArray.get(1);
                } catch (ClassCastException e) {
                    throw new JapiParseError("Invalid function definition");
                }

                var outputFields = new HashMap<String, FieldDeclaration>();
                for (var entry : outputDefinitionAsJsonJava.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration, typeDeclarationValue, false);
                    outputFields.put(result.fieldName, result.fieldDeclaration);
                }

                List<String> errors = List.of();
                if (definitionArray.size() >= 3) {
                    var errorDefinition = definitionArray.get(2);

                    try {
                        errors = (List<String>) errorDefinition;
                    } catch (ClassCastException e) {
                        throw new JapiParseError("Invalid function definition");
                    }

                    for (var errorDef : errors) {
                        if (!japiAsJsonJava.containsKey(errorDef)) {
                            throw new JapiParseError("Unknown error reference: %s".formatted(errorDef));
                        }
                    }
                }

                var inputStruct = new Struct("%s.input", inputFields);
                var outputStruct = new Struct("%s.output", outputFields);

                yield new FunctionDefinition(definitionKey, inputStruct, outputStruct, errors);
            }
            case "struct" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiParseError("Invalid struct definition");
                }

                Map<String, Object> structDefinitionAsJsonJava;
                try {
                    structDefinitionAsJsonJava = (Map<String, Object>) definitionArray.get(0);
                } catch (ClassCastException e) {
                    throw new JapiParseError("Invalid struct definition");
                }

                var fields = new HashMap<String, FieldDeclaration>();
                for (var entry : structDefinitionAsJsonJava.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration, typeDeclarationValue, false);
                    fields.put(result.fieldName, result.fieldDeclaration);
                }

                var type = new Struct(definitionKey, fields);

                yield new TypeDefinition(definitionKey, type);
            }
            case "error" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiParseError("Invalid error definition");
                }

                Map<String, Object> errorDefinitionAsJsonJava;
                try {
                    errorDefinitionAsJsonJava = (Map<String, Object>) definitionArray.get(0);
                } catch (ClassCastException e) {
                    throw new JapiParseError("Invalid error definition");
                }

                var fields = new HashMap<String, FieldDeclaration>();
                for (var entry : errorDefinitionAsJsonJava.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration, typeDeclarationValue, false);
                    fields.put(result.fieldName, result.fieldDeclaration);
                }

                yield new ErrorDefinition(definitionKey, fields);
            }
            case "enum" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiParseError("Invalid enum definition");
                }

                Map<String, Object> enumDefinitionAsJsonJava;
                try {
                    enumDefinitionAsJsonJava = (Map<String, Object>) definitionArray.get(0);
                } catch (ClassCastException e) {
                    throw new JapiParseError("Invalid enum definition");
                }

                var fields = new HashMap<String, FieldDeclaration>();
                for (var entry : enumDefinitionAsJsonJava.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration, typeDeclarationValue, true);
                    fields.put(result.fieldName, result.fieldDeclaration);
                }

                var type = new Enum(definitionKey, fields);

                yield new TypeDefinition(definitionKey, type);
            }
            case "title" -> {
                yield new TitleDefinition(definitionKey);
            }
            default -> throw new JapiParseError("Unrecognized japi keyword %s".formatted(keyword));
        };

        return parsedDefinition;
    }

    private static List<String> splitDefinitionKeywordAndName(String name) {
        var regex = Pattern.compile("^(struct|union|enum|error|function|event|title).([a-zA-Z_]+[a-zA-Z0-9_]*)$");
        var matcher = regex.matcher(name);
        matcher.find();
        var keyword = matcher.group(1);
        var partName = matcher.group(2);
        return List.of(keyword, partName);
    }

    private static FieldNameAndFieldDeclaration parseField(
            Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions,
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isForUnion
    ) {
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

    private static TypeDeclaration parseType(Map<String, List<Object>> japiAsJsonJava, Map<String, Definition> parsedDefinitions, String typeDeclaration) {
        var regex = Pattern.compile("^((null|boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct)\\.([a-zA-Z_]\\w*)))(\\?)?$");
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

        try {
            var name = matcher.group(7);
            if (name == null) {
                throw new RuntimeException("Ignore: will try another type");
            }

            var definition = parsedDefinitions.computeIfAbsent(name, (k) ->
                    parseDefinition(japiAsJsonJava, parsedDefinitions, typeDeclaration));
            if (definition instanceof TypeDefinition t) {
                return new TypeDeclaration(t.type, nullable);
            } else if (definition instanceof FunctionDefinition f) {
                throw new JapiParseError("Cannot reference a function in type declarations");
            } else if (definition instanceof ErrorDefinition e) {
                throw new JapiParseError("Cannot reference an error in type declarations");
            }
        } catch (Exception e) {
            if (e instanceof JapiParseError e1) {
                throw e1;
            }
        }

        throw new JapiParseError("Invalid type declaration: %s".formatted(typeDeclaration));
    }

}
