package uapi.internal.schema;

import static uapi.internal.schema.ParseFunctionType.parseFunctionType;
import static uapi.internal.schema.ParseStructType.parseStructType;
import static uapi.internal.schema.ParseUnionType.parseUnionType;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UAny;
import uapi.internal.types.UArray;
import uapi.internal.types.UBoolean;
import uapi.internal.types.UGeneric;
import uapi.internal.types.UInteger;
import uapi.internal.types.UMockCall;
import uapi.internal.types.UMockStub;
import uapi.internal.types.UNumber;
import uapi.internal.types.UObject;
import uapi.internal.types.USelect;
import uapi.internal.types.UString;
import uapi.internal.types.UType;

public class GetOrParseType {
    static UType getOrParseType(List<Object> path, String typeName, int thisTypeParameterCount,
            List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            List<SchemaParseFailure> allParseFailures,
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
            genericRegex = "|(T([%s]))"
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
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                        allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("union")) {
                type = parseUnionType(List.of(index), definition, customTypeName, List.of(), List.of(),
                        typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                        allParseFailures, failedTypes);
            } else if (customTypeName.startsWith("fn")) {
                type = parseFunctionType(List.of(index), definition, customTypeName,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, allParseFailures,
                        failedTypes);
            } else {
                UType possibleTypeExtension;
                switch (customTypeName) {
                    case "_ext.Select_":
                        possibleTypeExtension = new USelect(parsedTypes);
                        break;
                    case "_ext.Call_":
                        possibleTypeExtension = new UMockCall(parsedTypes);
                        break;
                    case "_ext.Stub_":
                        possibleTypeExtension = new UMockStub(parsedTypes);
                        break;
                    default:
                        possibleTypeExtension = null;
                }

                if (possibleTypeExtension == null) {
                    throw new UApiSchemaParseError(Arrays.asList(
                            new SchemaParseFailure(
                                    Collections.singletonList(index),
                                    "TypeExtensionImplementationMissing",
                                    Collections.singletonMap("name", customTypeName),
                                    null)));
                }

                type = possibleTypeExtension;
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
