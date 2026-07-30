//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.telepact.internal.schema.ParseTypeDeclaration.parseTypeDeclaration;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.TFieldDeclaration;
import io.github.telepact.internal.types.TType;

public class ParseField {
    static TFieldDeclaration parseField(
            List<Object> path,
            String fieldDeclaration,
            Object typeDeclarationValue,
            boolean isHeader,
            ParseContext ctx) {
        final var headerRegexString = "^@[a-z][a-zA-Z0-9_]*$";
        final var regexString = "^([a-z][a-zA-Z0-9_]*)(!)?$";
        final var regexToUse = isHeader ? headerRegexString : regexString;
        final var regex = Pattern.compile(regexToUse);

        final var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            final List<Object> finalPath = new ArrayList<>(path);
            finalPath.add(fieldDeclaration);

            throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, finalPath,
                    "KeyRegexMatchFailed", Map.of("regex", regexToUse))), ctx.telepactSchemaDocumentNamesToJson);
        }

        final var fieldName = matcher.group(0);
        final var optional = isHeader ? true : matcher.group(2) != null;

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(fieldName);

        final var typeDeclaration = parseTypeDeclaration(
                thisPath,
                typeDeclarationValue,
                ctx);

        return new TFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
