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

        var regexString = "^(.+?)(\\?)?$";
        var regex = Pattern.compile(regexString);
        var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", regexString))));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        boolean allowTraitsAndInfo = false;
        UType type = getOrParseType(basePath, typeName, thisTypeParameterCount, allowTraitsAndInfo, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions, allParseFailures, failedTypes);

        if (type instanceof UGeneric && nullable) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "NullableGenericDisallowed", Map.of())));
        }

        var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayLengthUnexpected",
                    Map.of("actual", typeDeclarationArray.size(), "expected", type.getTypeParameterCount() + 1))));
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
                parseFailures.addAll(_ParseSchemaUtil.getTypeUnexpectedValidationFailure(loopPath, e, "Array"));
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

        String genericRegex;
        if (thisTypeParameterCount > 0) {
            genericRegex = "|(T.([%s]))"
                    .formatted(thisTypeParameterCount > 1 ? "0-%d".formatted(thisTypeParameterCount - 1) : "0");
        } else {
            genericRegex = "";
        }

        String traitAndInfoRegex;
        if (allowTraitsAndInfo) {
            traitAndInfoRegex = "trait|info|";
        } else {
            traitAndInfoRegex = "";
        }

        var regexString = "^(boolean|integer|number|string|any|array|object)|((%sfn|(union|struct|ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)%s)$"
                .formatted(traitAndInfoRegex, genericRegex);
        var regex = Pattern.compile(regexString);
        var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "StringRegexMatchFailed", Map.of("regex", regexString))));
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
                default -> new UAny();
            };
        }

        if (thisTypeParameterCount > 0) {
            var genericParameterIndexString = matcher.group(9);
            var genericParameterIndex = Integer.parseInt(genericParameterIndexString);
            return new UGeneric(genericParameterIndex);
        }

        var customTypeName = matcher.group(2);
        if (customTypeName != null) {
            var index = schemaKeysToIndex.get(customTypeName);
            if (index == null) {
                throw new JApiSchemaParseError(List.of(new SchemaParseFailure(path,
                        "TypeUnknown", Map.of("name", customTypeName))));
            }
            var definition = (Map<String, Object>) originalJApiSchema.get(index);

            var typeParameterCountString = matcher.group(6);
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
