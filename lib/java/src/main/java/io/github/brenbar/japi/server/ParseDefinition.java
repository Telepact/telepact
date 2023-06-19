package io.github.brenbar.japi.server;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class ParseDefinition {

    static Definition parseDefinition(Map<String, List<Object>> japiAsJsonJava,
            Map<String, Definition> parsedDefinitions, String definitionKey) {
        var definitionAsJsonJavaWithDoc = japiAsJsonJava.get(definitionKey);
        if (definitionAsJsonJavaWithDoc == null) {
            throw new JapiParseError("Could not find definition for %s".formatted(definitionKey));
        }

        var regex = Pattern.compile("^(struct|union|enum|error|function|event|info).([a-zA-Z_]+[a-zA-Z0-9_]*)$");
        var matcher = regex.matcher(definitionKey);
        matcher.find();
        var keyword = matcher.group(1);
        var definitionName = matcher.group(2);

        var definitionAsJsonJava = definitionAsJsonJavaWithDoc.get(1);

        var parsedDefinition = switch (keyword) {
            case "function" -> {
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
                    var parsedField = ParseField.parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
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
                    var parsedField = ParseField.parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
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

                yield new FunctionDefinition(definitionKey, inputStruct, outputStruct, errors);
            }
            case "struct" -> {
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
                    var parsedField = ParseField.parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
                            typeDeclarationValue, false);
                    fields.put(parsedField.fieldName(), parsedField.fieldDeclaration());
                }

                var type = new Struct(definitionKey, fields);

                yield new TypeDefinition(definitionKey, type);
            }
            case "error" -> {
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
                    var parsedField = ParseField.parseField(japiAsJsonJava, parsedDefinitions, fieldDeclaration,
                            typeDeclarationValue, false);
                    fields.put(parsedField.fieldName(), parsedField.fieldDeclaration());
                }

                yield new ErrorDefinition(definitionKey, fields);
            }
            case "enum" -> {
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
                        var caseStructParsedField = ParseField.parseField(japiAsJsonJava, parsedDefinitions,
                                caseStructFieldDeclaration, caseStructTypeDeclarationValue, false);
                        fields.put(caseStructParsedField.fieldName(), caseStructParsedField.fieldDeclaration());
                    }
                    var struct = new Struct("%s.%s".formatted(definitionKey, enumCase), fields);
                    cases.put(enumCase, struct);
                }

                var type = new Enum(definitionKey, cases);

                yield new TypeDefinition(definitionKey, type);
            }
            case "info" -> {
                yield new TitleDefinition(definitionKey);
            }
            default -> throw new JapiParseError("Unrecognized japi keyword %s".formatted(keyword));
        };

        return parsedDefinition;
    }
}
