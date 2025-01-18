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
import uapi.internal.types.UInteger;
import uapi.internal.types.UMockCall;
import uapi.internal.types.UMockStub;
import uapi.internal.types.UNumber;
import uapi.internal.types.UObject;
import uapi.internal.types.USelect;
import uapi.internal.types.UString;
import uapi.internal.types.UType;

public class GetOrParseType {
    static UType getOrParseType(
            List<Object> path,
            String typeName,
            ParseContext ctx) {
        if (ctx.failedTypes.contains(typeName)) {
            throw new UApiSchemaParseError(List.of(), ctx.uApiSchemaDocumentNamesToJson);
        }

        final var existingType = ctx.parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        final var regexString = "^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$";

        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "StringRegexMatchFailed", Map.of("regex", regexString))), ctx.uApiSchemaDocumentNamesToJson);
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

        final var customTypeName = matcher.group(2);
        final var thisIndex = ctx.schemaKeysToIndex.get(customTypeName);
        final var thisDocumentName = ctx.schemaKeysToDocumentName.get(customTypeName);
        if (thisIndex == null) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "TypeUnknown", Map.of("name", customTypeName))), ctx.uApiSchemaDocumentNamesToJson);
        }
        final var definition = (Map<String, Object>) ctx.uApiSchemaDocumentsToPseudoJson.get(thisDocumentName)
                .get(thisIndex);

        try {
            final List<Object> thisPath = List.of(thisIndex);
            final UType type;
            if (customTypeName.startsWith("struct")) {
                type = parseStructType(thisPath, definition, customTypeName, List.of(),
                        ctx.copyWithNewDocumentName(thisDocumentName));
            } else if (customTypeName.startsWith("union")) {
                type = parseUnionType(thisPath, definition, customTypeName, List.of(),
                        List.of(),
                        ctx.copyWithNewDocumentName(thisDocumentName));
            } else if (customTypeName.startsWith("fn")) {
                type = parseFunctionType(thisPath, definition, customTypeName,
                        ctx.copyWithNewDocumentName(thisDocumentName));
            } else {
                UType possibleTypeExtension;
                switch (customTypeName) {
                    case "_ext.Select_":
                        possibleTypeExtension = new USelect();
                        break;
                    case "_ext.Call_":
                        possibleTypeExtension = new UMockCall(ctx.parsedTypes);
                        break;
                    case "_ext.Stub_":
                        possibleTypeExtension = new UMockStub(ctx.parsedTypes);
                        break;
                    default:
                        possibleTypeExtension = null;
                }

                if (possibleTypeExtension == null) {
                    throw new UApiSchemaParseError(Arrays.asList(
                            new SchemaParseFailure(
                                    ctx.documentName,
                                    Collections.singletonList(thisIndex),
                                    "TypeExtensionImplementationMissing",
                                    Collections.singletonMap("name", customTypeName))),
                            ctx.uApiSchemaDocumentNamesToJson);
                }

                type = possibleTypeExtension;
            }

            ctx.parsedTypes.put(customTypeName, type);

            return type;
        } catch (UApiSchemaParseError e) {
            ctx.allParseFailures.addAll(e.schemaParseFailures);
            ctx.failedTypes.add(customTypeName);
            throw new UApiSchemaParseError(List.of(), ctx.uApiSchemaDocumentNamesToJson);
        }
    }
}
