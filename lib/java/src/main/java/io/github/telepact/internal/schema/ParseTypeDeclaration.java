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

import static io.github.telepact.internal.schema.GetOrParseType.getOrParseType;
import static io.github.telepact.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.TArray;
import io.github.telepact.internal.types.TObject;
import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;

public class ParseTypeDeclaration {

    static TTypeDeclaration parseTypeDeclaration(
            List<Object> path,
            Object typeDeclarationObject,
            ParseContext ctx) {

        if (typeDeclarationObject instanceof String) {
            final String rootTypeString = (String) typeDeclarationObject;

            final var regexString = "^(.+?)(\\?)?$";
            final var regex = Pattern.compile(regexString);

            final var matcher = regex.matcher(rootTypeString);
            if (!matcher.find()) {
                throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                        "StringRegexMatchFailed", Map.of("regex", regexString))), ctx.telepactSchemaDocumentNamesToJson);
            }

            final var typeName = matcher.group(1);
            final var nullable = matcher.group(2) != null;

            final TType type = getOrParseType(path, typeName, ctx);

            if (type.getTypeParameterCount() != 0) {
                throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                        "ArrayLengthUnexpected",
                        Map.of("actual", 1, "expected", type.getTypeParameterCount() + 1))),
                        ctx.telepactSchemaDocumentNamesToJson);
            }

            return new TTypeDeclaration(type, nullable, Collections.emptyList());
        }

        else if (typeDeclarationObject instanceof List) {
            final List<Object> listObject = (List<Object>) typeDeclarationObject;

            if (listObject.size() != 1) {
                throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                        "ArrayLengthUnexpected", Map.of("actual", listObject.size(), "expected", 1))),
                        ctx.telepactSchemaDocumentNamesToJson);
            }

            final var elementTypeDeclaration = listObject.get(0);
            final List<Object> newPath = new ArrayList<>(path);
            newPath.add(0);

            final TType arrayType = new TArray();
            final TTypeDeclaration parsedElementType = parseTypeDeclaration(newPath, elementTypeDeclaration, ctx);

            return new TTypeDeclaration(arrayType, false, List.of(parsedElementType));
        }

        else if (typeDeclarationObject instanceof Map) {
            final Map<?, ?> mapObject = (Map<?, ?>) typeDeclarationObject;

            if (mapObject.size() != 1) {
                throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                        "ObjectSizeUnexpected", Map.of("actual", mapObject.size(), "expected", 1))),
                        ctx.telepactSchemaDocumentNamesToJson);
            }

            final var entry = mapObject.entrySet().iterator().next();
            final var key = entry.getKey();
            final var value = entry.getValue();

            if (!(key instanceof String) || !"string".equals(key)) {
                final var keyPath = new ArrayList<>(path);
                keyPath.add("key");
                throw new TelepactSchemaParseError(List.of(
                    new SchemaParseFailure(ctx.documentName, path,"RequiredObjectKeyMissing", Map.of("key", "string")),
                    new SchemaParseFailure(ctx.documentName, keyPath, "ObjectKeyDisallowed", Map.of())),
                    ctx.telepactSchemaDocumentNamesToJson);
            }

            final List<Object> newPath = new ArrayList<>(path);
            newPath.add(key);

            final TType objectType = new TObject();

            final TTypeDeclaration parsedValueType = parseTypeDeclaration(newPath, value, ctx);

            return new TTypeDeclaration(objectType, false, List.of(parsedValueType));
        }

        else {
            final List<SchemaParseFailure> failures = getTypeUnexpectedParseFailure(ctx.documentName, path,
                    typeDeclarationObject, "StringOrArrayOrObject");
            throw new TelepactSchemaParseError(failures, ctx.telepactSchemaDocumentNamesToJson);
        }
    }
}
