//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
//|

package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.ParseFunctionType.parseFunctionType;
import static io.github.telepact.internal.schema.ParseStructType.parseStructType;
import static io.github.telepact.internal.schema.ParseUnionType.parseUnionType;

import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.TAny;
import io.github.telepact.internal.types.TArray;
import io.github.telepact.internal.types.TBoolean;
import io.github.telepact.internal.types.TInteger;
import io.github.telepact.internal.types.TMockCall;
import io.github.telepact.internal.types.TMockStub;
import io.github.telepact.internal.types.TNumber;
import io.github.telepact.internal.types.TObject;
import io.github.telepact.internal.types.TSelect;
import io.github.telepact.internal.types.TString;
import io.github.telepact.internal.types.TType;

public class GetOrParseType {
    static TType getOrParseType(
            List<Object> path,
            String typeName,
            ParseContext ctx) {
        if (ctx.failedTypes.contains(typeName)) {
            throw new TelepactSchemaParseError(List.of(), ctx.telepactSchemaDocumentNamesToJson);
        }

        final var existingType = ctx.parsedTypes.get(typeName);
        if (existingType != null) {
            return existingType;
        }

        final var regexString = "^(boolean|integer|number|string|any|array|object)|((fn|(union|struct|_ext))\\.([a-zA-Z_]\\w*))$";

        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(typeName);
        if (!matcher.find()) {
            throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "StringRegexMatchFailed", Map.of("regex", regexString))), ctx.telepactSchemaDocumentNamesToJson);
        }

        final var standardTypeName = matcher.group(1);
        if (standardTypeName != null) {
            return switch (standardTypeName) {
                case "boolean" -> new TBoolean();
                case "integer" -> new TInteger();
                case "number" -> new TNumber();
                case "string" -> new TString();
                case "array" -> new TArray();
                case "object" -> new TObject();
                default -> new TAny();
            };
        }

        final var customTypeName = matcher.group(2);
        final var thisIndex = ctx.schemaKeysToIndex.get(customTypeName);
        final var thisDocumentName = ctx.schemaKeysToDocumentName.get(customTypeName);
        if (thisIndex == null) {
            throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "TypeUnknown", Map.of("name", customTypeName))), ctx.telepactSchemaDocumentNamesToJson);
        }
        final var definition = (Map<String, Object>) ctx.telepactSchemaDocumentsToPseudoJson.get(thisDocumentName)
                .get(thisIndex);

        try {
            final List<Object> thisPath = List.of(thisIndex);
            final TType type;
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
                TType possibleTypeExtension;
                switch (customTypeName) {
                    case "_ext.Select_":
                        possibleTypeExtension = new TSelect();
                        break;
                    case "_ext.Call_":
                        possibleTypeExtension = new TMockCall(ctx.parsedTypes);
                        break;
                    case "_ext.Stub_":
                        possibleTypeExtension = new TMockStub(ctx.parsedTypes);
                        break;
                    default:
                        possibleTypeExtension = null;
                }

                if (possibleTypeExtension == null) {
                    throw new TelepactSchemaParseError(Arrays.asList(
                            new SchemaParseFailure(
                                    ctx.documentName,
                                    Collections.singletonList(thisIndex),
                                    "TypeExtensionImplementationMissing",
                                    Collections.singletonMap("name", customTypeName))),
                            ctx.telepactSchemaDocumentNamesToJson);
                }

                type = possibleTypeExtension;
            }

            ctx.parsedTypes.put(customTypeName, type);

            return type;
        } catch (TelepactSchemaParseError e) {
            ctx.allParseFailures.addAll(e.schemaParseFailures);
            ctx.failedTypes.add(customTypeName);
            throw new TelepactSchemaParseError(List.of(), ctx.telepactSchemaDocumentNamesToJson);
        }
    }
}
