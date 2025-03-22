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
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.TType;
import io.github.telepact.internal.types.TTypeDeclaration;

public class ParseTypeDeclaration {
    static TTypeDeclaration parseTypeDeclaration(
            List<Object> path,
            List<Object> typeDeclarationArray,
            ParseContext ctx) {
        if (typeDeclarationArray.isEmpty()) {
            throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "EmptyArrayDisallowed", Map.of())), ctx.telepactSchemaDocumentNamesToJson);
        }

        final List<Object> basePath = new ArrayList<>(path);
        basePath.add(0);

        final var baseType = typeDeclarationArray.get(0);

        if (!(baseType instanceof String)) {
            final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, basePath,
                    baseType, "String");
            throw new TelepactSchemaParseError(thisParseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }
        final String rootTypeString = (String) baseType;

        final var regexString = "^(.+?)(\\?)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, basePath,
                    "StringRegexMatchFailed", Map.of("regex", regexString))), ctx.telepactSchemaDocumentNamesToJson);
        }

        final var typeName = matcher.group(1);
        final var nullable = matcher.group(2) != null;

        final TType type = getOrParseType(basePath, typeName, ctx);

        final var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, path,
                    "ArrayLengthUnexpected",
                    Map.of("actual", typeDeclarationArray.size(), "expected", type.getTypeParameterCount() + 1))),
                    ctx.telepactSchemaDocumentNamesToJson);
        }

        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var typeParameters = new ArrayList<TTypeDeclaration>();
        final var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());

        var index = 0;
        for (final var e : givenTypeParameters) {
            index += 1;

            final List<Object> loopPath = new ArrayList<>(path);
            loopPath.add(index);

            if (!(e instanceof List)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                        loopPath,
                        e,
                        "Array");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final TTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, (List<Object>) e, ctx);

                typeParameters.add(typeParameterTypeDeclaration);
            } catch (TelepactSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new TelepactSchemaParseError(parseFailures, ctx.telepactSchemaDocumentNamesToJson);
        }

        return new TTypeDeclaration(type, nullable, typeParameters);
    }
}
