package io.github.telepact.internal.schema;

import static io.github.telepact.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.telepact.internal.schema.ParseTypeDeclaration.parseTypeDeclaration;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.telepact.TelepactSchemaParseError;
import io.github.telepact.internal.types.VFieldDeclaration;
import io.github.telepact.internal.types.VType;

public class ParseField {
    static VFieldDeclaration parseField(
            List<Object> path,
            String fieldDeclaration,
            Object typeDeclarationValue,
            ParseContext ctx) {
        final var regexString = "^([a-z][a-zA-Z0-9_]*)(!)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(fieldDeclaration);
        if (!matcher.find()) {
            final List<Object> finalPath = new ArrayList<>(path);
            finalPath.add(fieldDeclaration);

            throw new TelepactSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, finalPath,
                    "KeyRegexMatchFailed", Map.of("regex", regexString))), ctx.telepactSchemaDocumentNamesToJson);
        }

        final var fieldName = matcher.group(0);
        final var optional = matcher.group(2) != null;

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(fieldName);

        if (!(typeDeclarationValue instanceof List)) {
            throw new TelepactSchemaParseError(
                    getTypeUnexpectedParseFailure(ctx.documentName, thisPath, typeDeclarationValue, "Array"),
                    ctx.telepactSchemaDocumentNamesToJson);
        }
        final List<Object> typeDeclarationArray = (List<Object>) typeDeclarationValue;

        final var typeDeclaration = parseTypeDeclaration(
                thisPath,
                typeDeclarationArray,
                ctx);

        return new VFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
