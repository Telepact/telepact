package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

public class _ParseSchemaTypeUtil {

    static UTypeDeclaration parseTypeDeclaration(List<Object> path, List<Object> typeDeclarationArray,
            int thisTypeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, TypeExtension> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (typeDeclarationArray.size() == 0) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayMustNotBeEmpty", Map.of())));
        }

        var basePath = _ValidateUtil.append(path, 0);

        var baseType = typeDeclarationArray.get(0);

        String rootTypeString;
        try {
            rootTypeString = (String) baseType;
        } catch (ClassCastException ex) {
            throw new JApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(basePath, baseType, "String"));
        }

        var regex = Pattern.compile("^(.*?)(\\?)?$");
        var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "CouldNotParseType", Map.of())));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        boolean allowTraitsAndInfo = false;
        UType type = getOrParseType(basePath, typeName, thisTypeParameterCount, allowTraitsAndInfo, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions, allParseFailures, failedTypes);

        if (type instanceof UGeneric && nullable) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "CannotMarkGenericAsNullable", Map.of())));
        }

        var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "IncorrectNumberOfTypeParameters", Map.of())));
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();
        var typeParameters = new ArrayList<UTypeDeclaration>();
        var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());
        var index = 0;
        for (var e : givenTypeParameters) {
            index += 1;
            var loopPath = _ValidateUtil.append(path, index);
            List<Object> l;
            try {
                l = (List<Object>) e;
            } catch (ClassCastException ex) {
                parseFailures.add(new SchemaParseFailure(loopPath,
                        "ArrayTypeRequired", Map.of()));
                continue;
            }

            UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, l, thisTypeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
                typeParameters.add(typeParameterTypeDeclaration);
            } catch (JApiSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        return new UTypeDeclaration(type, nullable, typeParameters);
    }

    static UType getOrParseType(List<Object> path, String typeName, int thisTypeParameterCount,
            boolean allowTraitsAndInfo,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, TypeExtension> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (failedTypes.contains(typeName)) {
            throw new JApiSchemaParseError(List.of());
        }

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

            try {
                UType type;
                if (customTypeName.startsWith("struct")) {
                    type = _ParseSchemaCustomTypeUtil.parseStructType(List.of(index), definition, customTypeName,
                            typeParameterCount,
                            originalJApiSchema,
                            schemaKeysToIndex, parsedTypes,
                            typeExtensions, allParseFailures, failedTypes);
                } else if (customTypeName.startsWith("union")) {
                    type = _ParseSchemaCustomTypeUtil.parseUnionType(List.of(index), definition, customTypeName,
                            typeParameterCount,
                            originalJApiSchema,
                            schemaKeysToIndex, parsedTypes,
                            typeExtensions, allParseFailures, failedTypes);
                } else if (customTypeName.startsWith("fn")) {
                    type = _ParseSchemaFnTypeUtil.parseFunctionType(List.of(index), definition, customTypeName,
                            originalJApiSchema,
                            schemaKeysToIndex, parsedTypes,
                            typeExtensions, false, allParseFailures, failedTypes);
                } else if (customTypeName.startsWith("ext")) {
                    var typeExtension = typeExtensions.get(customTypeName);
                    if (typeExtension == null) {
                        throw new JApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                                "TypeExtensionImplementationMissing", Map.of("type", customTypeName))));
                    }
                    type = new UExt(customTypeName, typeExtension, typeParameterCount);
                } else {
                    throw new JApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                            "InvalidType", Map.of("type", customTypeName))));
                }

                parsedTypes.put(customTypeName, type);

                return type;
            } catch (JApiSchemaParseError e) {
                allParseFailures.addAll(e.schemaParseFailures);
                failedTypes.add(customTypeName);
                throw new JApiSchemaParseError(List.of());
            }
        }

        throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                "InvalidType", Map.of("type", typeName))));
    }
}
