package io.github.msgpact.internal.schema;

import static io.github.msgpact.internal.schema.ParseFunctionType.parseFunctionType;
import static io.github.msgpact.internal.schema.ParseStructType.parseStructType;
import static io.github.msgpact.internal.schema.ParseUnionType.parseUnionType;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.msgpact.MsgPactSchemaParseError;
import io.github.msgpact.internal.types.VAny;
import io.github.msgpact.internal.types.VArray;
import io.github.msgpact.internal.types.VBoolean;
import io.github.msgpact.internal.types.VInteger;
import io.github.msgpact.internal.types.VMockCall;
import io.github.msgpact.internal.types.VMockStub;
import io.github.msgpact.internal.types.VNumber;
import io.github.msgpact.internal.types.VObject;
import io.github.msgpact.internal.types.VSelect;
import io.github.msgpact.internal.types.VString;
import io.github.msgpact.internal.types.VType;

public class GetOrParseType {
    static VType getOrParseType(
            List<Object> path,
            String typeName,
            ParseContext ctx) {
        if (ctx.failedTypes.contains(typeName)) {
            throw new MsgPactSchemaParseError(List.of(), ctx.msgPactSchemaDocumentNamesToJson);
        }

        final var existingType = ctx.parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        final var regexString = "^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$";

        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new MsgPactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "StringRegexMatchFailed", Map.of("regex", regexString))), ctx.msgPactSchemaDocumentNamesToJson);
        }

        final var standardTypeName = matcher.group(1);
        if (standardTypeName != null) {
            return switch (standardTypeName) {
                case "boolean" -> new VBoolean();
                case "integer" -> new VInteger();
                case "number" -> new VNumber();
                case "string" -> new VString();
                case "array" -> new VArray();
                case "object" -> new VObject();
                default -> new VAny();
            };
        }

        final var customTypeName = matcher.group(2);
        final var thisIndex = ctx.schemaKeysToIndex.get(customTypeName);
        final var thisDocumentName = ctx.schemaKeysToDocumentName.get(customTypeName);
        if (thisIndex == null) {
            throw new MsgPactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "TypeUnknown", Map.of("name", customTypeName))), ctx.msgPactSchemaDocumentNamesToJson);
        }
        final var definition = (Map<String, Object>) ctx.msgPactSchemaDocumentsToPseudoJson.get(thisDocumentName)
                .get(thisIndex);

        try {
            final List<Object> thisPath = List.of(thisIndex);
            final VType type;
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
                VType possibleTypeExtension;
                switch (customTypeName) {
                    case "_ext.Select_":
                        possibleTypeExtension = new VSelect();
                        break;
                    case "_ext.Call_":
                        possibleTypeExtension = new VMockCall(ctx.parsedTypes);
                        break;
                    case "_ext.Stub_":
                        possibleTypeExtension = new VMockStub(ctx.parsedTypes);
                        break;
                    default:
                        possibleTypeExtension = null;
                }

                if (possibleTypeExtension == null) {
                    throw new MsgPactSchemaParseError(Arrays.asList(
                            new SchemaParseFailure(
                                    ctx.documentName,
                                    Collections.singletonList(thisIndex),
                                    "TypeExtensionImplementationMissing",
                                    Collections.singletonMap("name", customTypeName))),
                            ctx.msgPactSchemaDocumentNamesToJson);
                }

                type = possibleTypeExtension;
            }

            ctx.parsedTypes.put(customTypeName, type);

            return type;
        } catch (MsgPactSchemaParseError e) {
            ctx.allParseFailures.addAll(e.schemaParseFailures);
            ctx.failedTypes.add(customTypeName);
            throw new MsgPactSchemaParseError(List.of(), ctx.msgPactSchemaDocumentNamesToJson);
        }
    }
}
