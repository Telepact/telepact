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
            Map<String, FieldDeclaration> inputFields,
            Map<String, FieldDeclaration> outputFields,
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

    public static class JapiDescriptionParseError extends RuntimeException {
        public JapiDescriptionParseError(String message) {
            super(message);
        }
    }

    public record ApiDescription(Map<String, Object> original, Map<String, Definition> parsed) {}

    public static ApiDescription newJapiDescription(String japiDescriptionJson) {
        var definitions = new HashMap<String, Definition>();

        var objectMapper = new ObjectMapper();
        Map<String, List<Object>> japiDescriptionJsonJava;
        try {
            japiDescriptionJsonJava = objectMapper.readValue(japiDescriptionJson, new TypeReference<Map<String, List<Object>>>(){});

            for (var entry : japiDescriptionJsonJava.entrySet()) {
                var defRefName = entry.getKey();
                if (!definitions.containsValue(defRefName)) {
                    var def = parseDefinition(japiDescriptionJsonJava, definitions, defRefName);
                    definitions.put(defRefName, def);
                }
            }
        } catch (IOException e) {
            throw new JapiDescriptionParseError("Invalid JSON: Document root must be an object");
        }

        return new ApiDescription((Map<String, Object>) (Object) japiDescriptionJsonJava, definitions);
    }

    private static Definition parseDefinition(Map<String, List<Object>> descriptionRoot, Map<String, Definition> definitions, String defRefName) {
        var description = descriptionRoot.get(defRefName);
        if (definitions == null) {
            throw new JapiDescriptionParseError("Could not find definition for %s".formatted(defRefName));
        }

        var splitName = splitJapiDefinitionName(defRefName);
        var keyword = splitName.get(0);
        var definitionName = splitName.get(1);

        var definitionArray = description.stream().filter(l -> !(l instanceof String)).collect(Collectors.toList());

        var def = switch (keyword) {
            case "function" -> {
                if (definitionArray.size() < 2) {
                    throw new JapiDescriptionParseError("function definition must be an array of 0 or more string elements followed by 2 object elements optionally followed by an array element");
                }
                var inputDefinition = definitionArray.get(0);

                Map<String, Object> inputDefinitionMap;
                try {
                    inputDefinitionMap = (Map<String, Object>) inputDefinition;
                } catch (ClassCastException e) {
                    throw new JapiDescriptionParseError("function definition must be an array of 0 or more string elements followed by 2 object elements optionally followed by an array element");
                }
                var inputFields = new HashMap<String, FieldDeclaration>();
                for (var entry : inputDefinitionMap.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(descriptionRoot, definitions, fieldDeclaration, typeDeclarationValue, false);
                    inputFields.put(result.fieldName, result.fieldDeclaration);
                }

                var outputDefinition = definitionArray.get(1);

                Map<String, Object> outputDefinitionMap;
                try {
                    outputDefinitionMap = (Map<String, Object>) outputDefinition;
                } catch (ClassCastException e) {
                    throw new JapiDescriptionParseError("function definition must be an array of 0 or more string elements followed by 2 object elements optionally followed by an array element");
                }

                var outputFields = new HashMap<String, FieldDeclaration>();
                for (var entry : outputDefinitionMap.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(descriptionRoot, definitions, fieldDeclaration, typeDeclarationValue, false);
                    outputFields.put(result.fieldName, result.fieldDeclaration);
                }

                List<String> errors = List.of();
                if (definitionArray.size() >= 3) {
                    var errorDefinition = definitionArray.get(2);

                    try {
                        errors = (List<String>) errorDefinition;
                    } catch (ClassCastException e) {
                        throw new JapiDescriptionParseError("function definition must be an array where if the final element is an array, it must be an array of strings");
                    }

                    for (var errorDef : errors) {
                        if (!descriptionRoot.containsKey(errorDef)) {
                            throw new JapiDescriptionParseError("Unknown error reference: %s".formatted(errorDef));
                        }
                    }
                }

                yield new FunctionDefinition(defRefName, inputFields, outputFields, errors);
            }
            case "struct" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiDescriptionParseError("struct definition must be an array of 0 or more string elements followed by 1 object element");
                }
                var definition = definitionArray.get(0);

                Map<String, Object> definitionsMap;
                try {
                    definitionsMap = (Map<String, Object>) definition;
                } catch (ClassCastException e) {
                    throw new JapiDescriptionParseError("struct definition must be an array of 0 or more string elements followed by 1 object element");
                }

                var fields = new HashMap<String, FieldDeclaration>();
                for (var entry : definitionsMap.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(descriptionRoot, definitions, fieldDeclaration, typeDeclarationValue, false);
                    fields.put(result.fieldName, result.fieldDeclaration);
                }

                var type = new Struct(defRefName, fields);

                yield new TypeDefinition(defRefName, type);
            }
            case "error" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiDescriptionParseError("error definition must be an array of 0 or more string elements followed by 1 object element");
                }
                var definition = definitionArray.get(0);

                Map<String, Object> definitionsMap;
                try {
                    definitionsMap = (Map<String, Object>) definition;
                } catch (ClassCastException e) {
                    throw new JapiDescriptionParseError("error definition must be an array of 0 or more string elements followed by 1 object element");
                }

                var fields = new HashMap<String, FieldDeclaration>();
                for (var entry : definitionsMap.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(descriptionRoot, definitions, fieldDeclaration, typeDeclarationValue, false);
                    fields.put(result.fieldName, result.fieldDeclaration);
                }

                yield new ErrorDefinition(defRefName, fields);
            }
            case "enum" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiDescriptionParseError("enum definition must be an array of 0 or more string elements followed by 1 object element");
                }

                var definition = definitionArray.get(0);

                Map<String, Object> definitionsMap;
                try {
                    definitionsMap = (Map<String, Object>) definition;
                } catch (ClassCastException e) {
                    throw new JapiDescriptionParseError("enum definition must be an array of 0 or more string elements followed by 1 object element");
                }

                var fields = new HashMap<String, FieldDeclaration>();
                for (var entry : definitionsMap.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(descriptionRoot, definitions, fieldDeclaration, typeDeclarationValue, true);
                    fields.put(result.fieldName, result.fieldDeclaration);
                }

                var type = new Enum(defRefName, fields);

                yield new TypeDefinition(defRefName, type);
            }
            case "title" -> {
                yield new TitleDefinition(defRefName);
            }
            default -> throw new JapiDescriptionParseError("Unrecognized japi keyword %s".formatted(keyword));
        };

        return def;
    }

    private static List<String> splitJapiDefinitionName(String name) {
        var regex = Pattern.compile("^(struct|union|enum|error|function|event|title).([a-zA-Z_]+[a-zA-Z0-9_]*)$");
        var matcher = regex.matcher(name);
        matcher.find();
        var keyword = matcher.group(1);
        var partName = matcher.group(2);
        return List.of(keyword, partName);
    }

    private static FieldNameAndFieldDeclaration parseField(
            Map<String, List<Object>> descriptionRoot,
            Map<String, Definition> definitions,
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
            throw new JapiDescriptionParseError("Union keys cannot be marked as optional");
        }

        String typeDeclarationString;
        try {
            typeDeclarationString = (String) typeDeclarationValue;
        } catch (ClassCastException e) {
            throw new JapiDescriptionParseError("Type declarations should be strings");
        }

        var typeDeclaration = parseType(descriptionRoot, definitions, typeDeclarationString);

        return new FieldNameAndFieldDeclaration(fieldName, new FieldDeclaration(typeDeclaration, optional));
    }

    private static TypeDeclaration parseType(Map<String, List<Object>> descriptionRoot, Map<String, Definition> definitions, String typeDeclaration) {
        var typeDefRegex = Pattern.compile("^((null|boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct)\\.([a-zA-Z_]\\w*)))(\\?)?$");
        var matcher = typeDefRegex.matcher(typeDeclaration);
        matcher.find();

        boolean nullable = matcher.group(10) != null;

        try {
            var name = matcher.group(2);
            if (name == null) {
                throw new RuntimeException();
            }
            var type = switch (name) {
                case "null" -> new JsonNull();
                case "boolean" -> new JsonBoolean();
                case "integer" -> new JsonInteger();
                case "number" -> new JsonNumber();
                case "string" -> new JsonString();
                case "any" -> new JsonAny();
                default -> throw new JapiDescriptionParseError("Unrecognized type: %s".formatted(name));
            };

            if (type instanceof JsonNull) {
                nullable = true;
            }

            return new TypeDeclaration(type, nullable);
        } catch (Exception e) {
            if (e instanceof JapiDescriptionParseError e1) {
                throw e1;
            }
        }

        try {
            var name = matcher.group(4);
            if (name == null) {
                throw new RuntimeException();
            }

            var nestedName = matcher.group(6);

            TypeDeclaration nestedType;
            if (nestedName != null) {
                nestedType = parseType(descriptionRoot, definitions, nestedName);
            } else {
                nestedType = new TypeDeclaration(new JsonAny(), false);
            }

            var type = switch (name) {
                case "array" -> new JsonArray(nestedType);
                case "object" -> new JsonObject(nestedType);
                default -> throw new JapiDescriptionParseError("Unrecognized type: %s".formatted(name));
            };

            return new TypeDeclaration(type, nullable);
        } catch (Exception e) {
            if (e instanceof JapiDescriptionParseError e1) {
                throw e1;
            }
        }

        try {
            var name = matcher.group(7);
            if (name == null) {
                throw new RuntimeException();
            }

            var definition = definitions.computeIfAbsent(name, (k) ->
                    parseDefinition(descriptionRoot, definitions, typeDeclaration));
            if (definition instanceof TypeDefinition t) {
                return new TypeDeclaration(t.type, nullable);
            } else if (definition instanceof FunctionDefinition f) {
                throw new JapiDescriptionParseError("Cannot reference a function in type declarations");
            }
        } catch (Exception e) {
            if (e instanceof JapiDescriptionParseError e1) {
                throw e1;
            }
        }

        throw new JapiDescriptionParseError("Invalid type declaration: %s".formatted(typeDeclaration));
    }

}
