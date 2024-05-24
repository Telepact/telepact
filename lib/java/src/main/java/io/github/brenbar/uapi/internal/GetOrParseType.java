package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UAny;
import io.github.brenbar.uapi.internal.types.UArray;
import io.github.brenbar.uapi.internal.types.UBoolean;
import io.github.brenbar.uapi.internal.types.UGeneric;
import io.github.brenbar.uapi.internal.types.UInteger;
import io.github.brenbar.uapi.internal.types.UNumber;
import io.github.brenbar.uapi.internal.types.UObject;
import io.github.brenbar.uapi.internal.types.UString;
import io.github.brenbar.uapi.internal.types.UType;

import static io.github.brenbar.uapi.internal.ParseStructType.parseStructType;
import static io.github.brenbar.uapi.internal.ParseUnionType.parseUnionType;
import static io.github.brenbar.uapi.internal.ParseFunctionType.parseFunctionType;

public class GetOrParseType {
    static UType getOrParseType(List<Object> path, String typeName, int thisTypeParameterCount,
            List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, UType> typeExtensions, List<SchemaParseFailure> allParseFailures,
            Set<String> failedTypes) {
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
                    "StringRegexMatchFailed", Map.of("regex", regexString), null)));
        }

        final var standardTypeName = matcher.group(1);
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
            final var genericParameterIndexString = matcher.group(9);
            if (genericParameterIndexString != null) {
                final var genericParameterIndex = Integer.parseInt(genericParameterIndexString);
                return new UGeneric(genericParameterIndex);
            }
        }

        final var customTypeName = matcher.group(2);
        final var index = schemaKeysToIndex.get(customTypeName);
        if (index == null) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "TypeUnknown", Map.of("name", customTypeName), null)));
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
            final UType type;
            if (customTypeName.startsWith("struct")) {
                type = parseStructType(List.of(index), definition, customTypeName, List.of(),
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions,
                        allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("union")) {
                type = parseUnionType(List.of(index), definition, customTypeName, List.of(), List.of(),
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                        typeExtensions, allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("fn")) {
                type = parseFunctionType(List.of(index), definition, customTypeName,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);
            } else {
                type = typeExtensions.get(customTypeName);
                if (type == null) {
                    throw new UApiSchemaParseError(List.of(new SchemaParseFailure(List.of(index),
                            "TypeExtensionImplementationMissing", Map.of("name", customTypeName), null)));
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
