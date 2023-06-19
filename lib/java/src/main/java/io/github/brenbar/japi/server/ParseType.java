package io.github.brenbar.japi.server;

import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class ParseType {
    static TypeDeclaration parseType(Map<String, List<Object>> japiAsJsonJava,
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

        try {
            var name = matcher.group(7);
            if (name == null) {
                throw new RuntimeException("Ignore: will try another type");
            }

            var definition = parsedDefinitions.computeIfAbsent(name,
                    (k) -> ParseDefinition.parseDefinition(japiAsJsonJava, parsedDefinitions, typeDeclaration));
            if (definition instanceof TypeDefinition t) {
                return new TypeDeclaration(t.type(), nullable);
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
