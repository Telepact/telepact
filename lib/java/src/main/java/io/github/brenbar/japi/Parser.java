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

    public interface Type {}

    public static class JsonNull implements Type {}
    public static class JsonBoolean implements Type {}
    public static class JsonInteger implements Type {}
    public static class JsonNumber implements Type {}
    public static class JsonString implements Type {}
    public record JsonArray(TypeDeclaration nestedType) implements Type {}
    public record JsonObject(TypeDeclaration nestedType) implements Type {}
    public record Struct(Map<String, FieldDeclaration> fields) implements Type {}
    public record Union(Map<String, FieldDeclaration> cases) implements Type {}
    public record Enum(List<String> allowedValues) implements Type {}
    public static class JsonAny implements Type {}


    public record TypeDeclaration(
        Type type,
        boolean nullable
    ) {}

    public interface Definition {
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
    ) implements Definition {}

    public record TypeDefinition(
        String name,
        Type type
    ) implements Definition {}

    public record ErrorDefinition(
            String name,
            Map<String, FieldDeclaration> fields
    ) implements Definition {}

    private record FieldNameAndFieldDeclaration(
            String fieldName,
            FieldDeclaration fieldDeclaration
    ) {}

    public static class JapiDescriptionParseError extends RuntimeException {
        public JapiDescriptionParseError(String message) {
            super(message);
        }
    }

    public static Map<String, Definition> newJapiDescription(String japiDescriptionJson) {
        var descriptions = new HashMap<String, Definition>();

        var objectMapper = new ObjectMapper();
        try {
            var japiDescriptionJsonMap = objectMapper.readValue(japiDescriptionJson, new TypeReference<Map<String, List<Object>>>(){});

            for (var entry : japiDescriptionJsonMap.entrySet()) {
                var defRefName = entry.getKey();
                if (descriptions.containsValue(defRefName)) {
                    parseDefinition(japiDescriptionJsonMap, descriptions, defRefName);
                }
            }
        } catch (IOException e) {
            throw new JapiDescriptionParseError("Invalid JSON: Document root must be an object");
        }

        return descriptions;
    }

    private static void parseDefinition(Map<String, List<Object>> descriptionRoot, Map<String, Definition> definitions, String defRefName) {
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

                yield new FunctionDefinition(definitionName, inputFields, outputFields, errors);
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

                var type = new Struct(fields);

                yield new TypeDefinition(definitionName, type);
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

                yield new ErrorDefinition(definitionName, fields);
            }
            case "union" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiDescriptionParseError("union definition must be an array of 0 or more string elements followed by 1 object element");
                }

                var definition = definitionArray.get(0);

                Map<String, Object> definitionsMap;
                try {
                    definitionsMap = (Map<String, Object>) definition;
                } catch (ClassCastException e) {
                    throw new JapiDescriptionParseError("union definition must be an array of 0 or more string elements followed by 1 object element");
                }

                var fields = new HashMap<String, FieldDeclaration>();
                for (var entry : definitionsMap.entrySet()) {
                    var fieldDeclaration = entry.getKey();
                    var typeDeclarationValue = entry.getValue();
                    var result = parseField(descriptionRoot, definitions, fieldDeclaration, typeDeclarationValue, true);
                    fields.put(result.fieldName, result.fieldDeclaration);
                }

                var type = new Union(fields);

                yield new TypeDefinition(definitionName, type);
            }
            case "enum" -> {
                if (definitionArray.size() < 1) {
                    throw new JapiDescriptionParseError("enum definition must be an array of 0 or more string elements followed by 1 array element");
                }
                var definition = definitionArray.get(0);

                List<String> values;
                try {
                    values = (List<String>) definition;
                } catch (ClassCastException e) {
                    throw new JapiDescriptionParseError("enum definition must be an array of 0 or more string elements followed by 1 array element");
                }

                var type = new Enum(values);

                yield new TypeDefinition(definitionName, type);
            }
            default -> throw new JapiDescriptionParseError("Unrecognized japi keyword %s".formatted(keyword));
        };

        definitions.put(defRefName, def);
    }

    private static List<String> splitJapiDefinitionName(String name) {
        var regex = Pattern.compile("^(struct|union|enum|error|function|event).([a-zA-Z_]+[a-zA-Z0-9_]*)$");
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
        var typeDefRegex = Pattern.compile("^((boolean|integer|number|string|any)|((array|object)(<(.*)>)?)|((enum|struct|union)\\.([a-zA-Z_]+[a-zA-Z0-9_])*))(\\?)?$");
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
                nestedType = parseType(descriptionRoot, definitions, typeDeclaration);
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

            var definition = definitions.get(name);
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
