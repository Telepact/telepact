package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaTypeUtil {

    static _UTypeDeclaration parseTypeDeclaration(List<Object> path, List<Object> typeDeclarationArray,
            int thisTypeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (typeDeclarationArray.size() == 0) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "EmptyArrayDisallowed", Map.of())));
        }

        var basePath = _ValidateUtil.append(path, 0);

        var baseType = typeDeclarationArray.get(0);

        String rootTypeString;
        try {
            rootTypeString = _CastUtil.asString(baseType);
        } catch (ClassCastException e) {
            throw new UApiSchemaParseError(
                    _ParseSchemaUtil.getTypeUnexpectedValidationFailure(basePath, baseType, "String"));
        }

        var regexString = "^(.+?)(\\?)?$";
        var regex = Pattern.compile(regexString);
        var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", regexString))));
        }

        var typeName = matcher.group(1);
        var nullable = matcher.group(2) != null;

        _UType type = getOrParseType(basePath, typeName, thisTypeParameterCount, originalJApiSchema,
                schemaKeysToIndex, parsedTypes,
                typeExtensions, allParseFailures, failedTypes);

        if (type instanceof _UGeneric && nullable) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", "^(.+?)[^\\?]$"))));
        }

        var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayLengthUnexpected",
                    Map.of("actual", typeDeclarationArray.size(), "expected", type.getTypeParameterCount() + 1))));
        }

        var parseFailures = new ArrayList<SchemaParseFailure>();
        var typeParameters = new ArrayList<_UTypeDeclaration>();
        var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());
        var index = 0;
        for (var e : givenTypeParameters) {
            index += 1;
            var loopPath = _ValidateUtil.append(path, index);
            List<Object> l;
            try {
                l = _CastUtil.asList(e);
            } catch (ClassCastException e1) {
                parseFailures.addAll(_ParseSchemaUtil.getTypeUnexpectedValidationFailure(loopPath, e, "Array"));
                continue;
            }

            _UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, l, thisTypeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
                typeParameters.add(typeParameterTypeDeclaration);
            } catch (UApiSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new _UTypeDeclaration(type, nullable, typeParameters);
    }

    static _UType getOrParseType(List<Object> path, String typeName, int thisTypeParameterCount,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (failedTypes.contains(typeName)) {
            throw new UApiSchemaParseError(List.of());
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

        var regexString = "^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)%s)$"
                .formatted(genericRegex);
        var regex = Pattern.compile(regexString);
        var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "StringRegexMatchFailed", Map.of("regex", regexString))));
        }

        var standardTypeName = matcher.group(1);
        if (standardTypeName != null) {
            return switch (standardTypeName) {
                case "boolean" -> new _UBoolean();
                case "integer" -> new _UInteger();
                case "number" -> new _UNumber();
                case "string" -> new _UString();
                case "array" -> new _UArray();
                case "object" -> new _UObject();
                default -> new _UAny();
            };
        }

        if (thisTypeParameterCount > 0) {
            var genericParameterIndexString = matcher.group(9);
            var genericParameterIndex = Integer.parseInt(genericParameterIndexString);
            return new _UGeneric(genericParameterIndex);
        }

        var customTypeName = matcher.group(2);
        var index = schemaKeysToIndex.get(customTypeName);
        if (index == null) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "TypeUnknown", Map.of("name", customTypeName))));
        }
        var definition = (Map<String, Object>) originalJApiSchema.get(index);

        var typeParameterCountString = matcher.group(6);
        int typeParameterCount = 0;
        if (typeParameterCountString != null) {
            typeParameterCount = Integer.parseInt(typeParameterCountString);
        }

        try {
            _UType type;
            if (customTypeName.startsWith("struct")) {
                type = _ParseSchemaCustomTypeUtil.parseStructType(List.of(index), definition, customTypeName,
                        typeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("union")) {
                boolean okCaseRequired = false;
                type = _ParseSchemaCustomTypeUtil.parseUnionType(List.of(index), definition, customTypeName,
                        okCaseRequired, typeParameterCount,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("fn")) {
                type = _ParseSchemaFnTypeUtil.parseFunctionType(List.of(index), definition, customTypeName,
                        originalJApiSchema,
                        schemaKeysToIndex, parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
            } else {
                var typeExtension = typeExtensions.get(customTypeName);
                if (typeExtension == null) {
                    throw new UApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                            "TypeExtensionImplementationMissing", Map.of("name", customTypeName))));
                }
                type = new _UExt(customTypeName, typeExtension, typeParameterCount);
            }

            parsedTypes.put(customTypeName, type);

            return type;
        } catch (UApiSchemaParseError e) {
            allParseFailures.addAll(e.schemaParseFailures);
            failedTypes.add(customTypeName);
            throw new UApiSchemaParseError(List.of());
        }
    }
}
