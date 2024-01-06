package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

public class _ParseSchemaTypeUtil {

    static UTypeDeclaration parseTypeDeclaration(String path, List<Object> typeDeclarationArray,
            int thisTypeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, TypeExtension> typeExtensions) {
        if (typeDeclarationArray.size() == 0) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayMustNotBeEmpty", Map.of())));
        }

        var thisPath = "%s[%d]".formatted(path, 0);

        String rootTypeString;
        try {
            rootTypeString = (String) typeDeclarationArray.get(0);
        } catch (ClassCastException ex) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(thisPath,
                    "StringTypeRequired", Map.of())));
        }

        var regex = Pattern.compile("^(.*?)(\\?)?$");
        var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(thisPath,
                    "CouldNotParseType", Map.of())));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        boolean allowTraitsAndInfo = false;
        var type = getOrParseType(thisPath, typeName, thisTypeParameterCount, allowTraitsAndInfo, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions);

        if (type instanceof UGeneric && nullable) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(thisPath,
                    "CannotMarkGenericAsNullable", Map.of())));
        }

        var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "IncorrectNumberOfTypeParameters", Map.of())));
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();
        var typeParameters = new ArrayList<UTypeDeclaration>();
        var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());
        var index = 0;
        for (var e : givenTypeParameters) {
            var loopPath = "%s[%d]".formatted(path, index);
            index += 1;
            List<Object> l;
            try {
                l = (List<Object>) e;
            } catch (ClassCastException ex) {
                parseFailures.add(new SchemaParseFailure("%s[%d]".formatted(path, index),
                        "ArrayTypeRequired", Map.of()));
                continue;
            }

            UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, l, thisTypeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes, typeExtensions);
            } catch (JApiSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
                continue;
            }

            typeParameters.add(typeParameterTypeDeclaration);
        }

        return new UTypeDeclaration(type, nullable, typeParameters);
    }

    static UType getOrParseType(String path, String typeName, int thisTypeParameterCount,
            boolean allowTraitsAndInfo,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, TypeExtension> typeExtensions) {
        var existingType = parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        var regex = Pattern.compile(
                "^(boolean|integer|number|string|any|array|object|T.([0-2]))|((trait|info|fn|(union|struct|ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*))$");
        var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "InvalidType", Map.of("type", typeName))));
        }

        var standardTypeName = matcher.group(1);
        if (standardTypeName != null) {
            return switch (standardTypeName) {
                case "boolean" -> new UBoolean();
                case "integer" -> new UInteger();
                case "number" -> new UNumber();
                case "string" -> new UString();
                case "array" -> new UArray();
                case "object" -> new UObject();
                case "any" -> new UAny();
                default -> {
                    var genericParameterIndexString = matcher.group(2);
                    if (genericParameterIndexString != null) {
                        var genericParameterIndex = Integer.parseInt(genericParameterIndexString);
                        if (genericParameterIndex >= thisTypeParameterCount) {
                            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                                    "MaximumTypeParametersExceeded", Map.of())));
                        }
                        yield new UGeneric(genericParameterIndex);
                    } else {
                        throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                                "InvalidGenericType", Map.of("type", standardTypeName))));
                    }
                }
            };
        }

        var customTypeName = matcher.group(3);
        if (customTypeName != null) {
            var index = schemaKeysToIndex.get(customTypeName);
            if (index == null) {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                        "UndefinedType", Map.of("type", customTypeName))));
            }
            var definition = (Map<String, Object>) originalJApiSchema.get(index);

            var typeParameterCountString = matcher.group(7);
            int typeParameterCount = 0;
            if (typeParameterCountString != null) {
                typeParameterCount = Integer.parseInt(typeParameterCountString);
            }

            UType type;
            if (customTypeName.startsWith("struct")) {
                type = _ParseSchemaCustomTypeUtil.parseStructType(definition, customTypeName, typeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions);
            } else if (customTypeName.startsWith("union")) {
                type = _ParseSchemaCustomTypeUtil.parseUnionType(definition, customTypeName, typeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions);
            } else if (customTypeName.startsWith("fn")) {
                type = _ParseSchemaFnTypeUtil.parseFunctionType(definition, customTypeName, originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions, false);
            } else if (customTypeName.startsWith("ext")) {
                var typeExtension = typeExtensions.get(customTypeName);
                if (typeExtension == null) {
                    throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                            "TypeExtensionImplementationMissing", Map.of("type", customTypeName))));
                }
                type = new UExt(customTypeName, typeExtension, typeParameterCount);
            } else {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                        "InvalidType", Map.of("type", customTypeName))));
            }

            parsedTypes.put(customTypeName, type);

            return type;
        }

        throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                "InvalidType", Map.of("type", typeName))));
    }
}
