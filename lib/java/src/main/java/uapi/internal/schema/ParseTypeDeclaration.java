package uapi.internal.schema;

import static uapi.internal.schema.GetOrParseType.getOrParseType;
import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UType;
import uapi.internal.types.UTypeDeclaration;

public class ParseTypeDeclaration {
    static UTypeDeclaration parseTypeDeclaration(
            List<Object> typeDeclarationArray,
            ParseContext ctx) {
        if (typeDeclarationArray.isEmpty()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, ctx.path,
                    "EmptyArrayDisallowed", Map.of())), ctx.uApiSchemaDocumentNamesToJson);
        }

        final List<Object> basePath = new ArrayList<>(ctx.path);
        basePath.add(0);

        final var baseType = typeDeclarationArray.get(0);

        if (!(baseType instanceof String)) {
            final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName, basePath,
                    baseType, "String");
            throw new UApiSchemaParseError(thisParseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }
        final String rootTypeString = (String) baseType;

        final var regexString = "^(.+?)(\\?)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, basePath,
                    "StringRegexMatchFailed", Map.of("regex", regexString))), ctx.uApiSchemaDocumentNamesToJson);
        }

        final var typeName = matcher.group(1);
        final var nullable = matcher.group(2) != null;

        final UType type = getOrParseType(typeName,
                ctx.copyWithNewPath(basePath));

        final var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(ctx.documentName, ctx.path,
                    "ArrayLengthUnexpected",
                    Map.of("actual", typeDeclarationArray.size(), "expected", type.getTypeParameterCount() + 1))),
                    ctx.uApiSchemaDocumentNamesToJson);
        }

        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var typeParameters = new ArrayList<UTypeDeclaration>();
        final var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());

        var index = 0;
        for (final var e : givenTypeParameters) {
            index += 1;

            final List<Object> loopPath = new ArrayList<>(ctx.path);
            loopPath.add(index);

            if (!(e instanceof List)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(ctx.documentName,
                        loopPath,
                        e,
                        "Array");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration((List<Object>) e, ctx.copyWithNewPath(loopPath));

                typeParameters.add(typeParameterTypeDeclaration);
            } catch (UApiSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, ctx.uApiSchemaDocumentNamesToJson);
        }

        return new UTypeDeclaration(type, nullable, typeParameters);
    }
}
