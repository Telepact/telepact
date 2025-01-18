package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseTypeDeclaration.parseTypeDeclaration;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFieldDeclaration;
import uapi.internal.types.UType;

public class ParseField {
    static UFieldDeclaration parseField(
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

            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, finalPath,
                    "KeyRegexMatchFailed", Map.of("regex", regexString))), ctx.uApiSchemaDocumentNamesToJson);
        }

        final var fieldName = matcher.group(0);
        final var optional = matcher.group(2) != null;

        final List<Object> thisPath = new ArrayList<>(path);
        thisPath.add(fieldName);

        if (!(typeDeclarationValue instanceof List)) {
            throw new UApiSchemaParseError(
                    getTypeUnexpectedParseFailure(ctx.documentName, thisPath, typeDeclarationValue, "Array"),
                    ctx.uApiSchemaDocumentNamesToJson);
        }
        final List<Object> typeDeclarationArray = (List<Object>) typeDeclarationValue;

        final var typeDeclaration = parseTypeDeclaration(
                thisPath,
                typeDeclarationArray,
                ctx);

        return new UFieldDeclaration(fieldName, typeDeclaration, optional);
    }
}
