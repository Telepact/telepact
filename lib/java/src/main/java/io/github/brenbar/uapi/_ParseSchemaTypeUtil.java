package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaTypeUtil {

    static _UTypeDeclaration parseTypeDeclaration(List<Object> path, List<Object> typeDeclarationArray,
            int thisTypeParameterCount, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (typeDeclarationArray.size() == 0) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "EmptyArrayDisallowed", Map.of())));
        }

        final List<Object> basePath = _ValidateUtil.append(path, 0);
        final var baseType = typeDeclarationArray.get(0);

        final String rootTypeString;
        try {
            rootTypeString = _CastUtil.asString(baseType);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> thisParseFailures = _ParseSchemaUtil
                    .getTypeUnexpectedValidationFailure(basePath, baseType, "String");
            throw new UApiSchemaParseError(thisParseFailures);
        }

        final var regexString = "^(.+?)(\\?)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", regexString))));
        }

        final var typeName = matcher.group(1);
        final var nullable = matcher.group(2) != null;

        final _UType type = getOrParseType(basePath, typeName, thisTypeParameterCount, uApiSchemaPseudoJson,
                schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);

        if (type instanceof _UGeneric && nullable) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", "^(.+?)[^\\?]$"))));
        }

        final var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayLengthUnexpected",
                    Map.of("actual", typeDeclarationArray.size(), "expected", type.getTypeParameterCount() + 1))));
        }

        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var typeParameters = new ArrayList<_UTypeDeclaration>();
        final var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());

        var index = 0;
        for (final var e : givenTypeParameters) {
            index += 1;
            final List<Object> loopPath = _ValidateUtil.append(path, index);

            final List<Object> l;
            try {
                l = _CastUtil.asList(e);
            } catch (ClassCastException e1) {
                final List<SchemaParseFailure> thisParseFailures = _ParseSchemaUtil
                        .getTypeUnexpectedValidationFailure(loopPath, e, "Array");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final _UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, l, thisTypeParameterCount,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);

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
            List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (failedTypes.contains(typeName)) {
            throw new UApiSchemaParseError(List.of());
        }

        final var existingType = parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        final String genericRegex;
        if (thisTypeParameterCount > 0) {
            genericRegex = "|(T.([%s]))"
                    .formatted(thisTypeParameterCount > 1 ? "0-%d".formatted(thisTypeParameterCount - 1) : "0");
        } else {
            genericRegex = "";
        }

        final var regexString = "^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext)(<([1-3])>)?)\\.([a-zA-Z_]\\w*)%s)$"
                .formatted(genericRegex);
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "StringRegexMatchFailed", Map.of("regex", regexString))));
        }

        final var standardTypeName = matcher.group(1);
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
            final var genericParameterIndexString = matcher.group(9);
            final var genericParameterIndex = Integer.parseInt(genericParameterIndexString);
            return new _UGeneric(genericParameterIndex);
        }

        final var customTypeName = matcher.group(2);
        final var index = schemaKeysToIndex.get(customTypeName);
        if (index == null) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "TypeUnknown", Map.of("name", customTypeName))));
        }
        final var definition = (Map<String, Object>) uApiSchemaPseudoJson.get(index);

        final var typeParameterCountString = matcher.group(6);
        final int typeParameterCount;
        if (typeParameterCountString != null) {
            typeParameterCount = Integer.parseInt(typeParameterCountString);
        } else {
            typeParameterCount = 0;
        }

        try {
            final _UType type;
            if (customTypeName.startsWith("struct")) {
                final var isForFn = false;
                type = _ParseSchemaCustomTypeUtil.parseStructType(List.of(index), definition, customTypeName, isForFn,
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions,
                        allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("union")) {
                final var isForFn = false;
                type = _ParseSchemaCustomTypeUtil.parseUnionType(List.of(index), definition, customTypeName, isForFn,
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("fn")) {
                type = _ParseSchemaFnTypeUtil.parseFunctionType(List.of(index), definition, customTypeName,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);
            } else {
                type = typeExtensions.get(customTypeName);
                if (type == null) {
                    throw new UApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                            "TypeExtensionImplementationMissing", Map.of("name", customTypeName))));
                }
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
