package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UGeneric;
import io.github.brenbar.uapi.internal.types.UType;
import io.github.brenbar.uapi.internal.types.UTypeDeclaration;

import static io.github.brenbar.uapi.internal.GetType.getType;
import static io.github.brenbar.uapi.internal.Append.append;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.AsString.asString;
import static io.github.brenbar.uapi.internal.AsList.asList;
import static io.github.brenbar.uapi.internal.GetOrParseType.getOrParseType;

public class ParseTypeDeclaration {
    static UTypeDeclaration parseTypeDeclaration(List<Object> path, List<Object> typeDeclarationArray,
            int thisTypeParameterCount, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        if (typeDeclarationArray.isEmpty()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "EmptyArrayDisallowed", Map.of(), null)));
        }

        final List<Object> basePath = append(path, 0);
        final var baseType = typeDeclarationArray.get(0);

        final String rootTypeString;
        try {
            rootTypeString = asString(baseType);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(basePath,
                    baseType, "String");
            throw new UApiSchemaParseError(thisParseFailures);
        }

        final var regexString = "^(.+?)(\\?)?$";
        final var regex = Pattern.compile(regexString);

        final var matcher = regex.matcher(rootTypeString);
        if (!matcher.find()) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", regexString), null)));
        }

        final var typeName = matcher.group(1);
        final var nullable = matcher.group(2) != null;

        final UType type = getOrParseType(basePath, typeName, thisTypeParameterCount, uApiSchemaPseudoJson,
                schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);

        if (type instanceof UGeneric && nullable) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(basePath,
                    "StringRegexMatchFailed", Map.of("regex", "^(.+?)[^\\?]$"), null)));
        }

        final var givenTypeParameterCount = typeDeclarationArray.size() - 1;
        if (type.getTypeParameterCount() != givenTypeParameterCount) {
            throw new UApiSchemaParseError(List.of(new SchemaParseFailure(path,
                    "ArrayLengthUnexpected",
                    Map.of("actual", typeDeclarationArray.size(), "expected", type.getTypeParameterCount() + 1),
                    null)));
        }

        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var typeParameters = new ArrayList<UTypeDeclaration>();
        final var givenTypeParameters = typeDeclarationArray.subList(1, typeDeclarationArray.size());

        var index = 0;
        for (final var e : givenTypeParameters) {
            index += 1;
            final List<Object> loopPath = append(path, index);

            final List<Object> l;
            try {
                l = asList(e);
            } catch (ClassCastException e1) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(loopPath, e,
                        "Array");

                parseFailures.addAll(thisParseFailures);
                continue;
            }

            final UTypeDeclaration typeParameterTypeDeclaration;
            try {
                typeParameterTypeDeclaration = parseTypeDeclaration(loopPath, l, thisTypeParameterCount,
                        uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures,
                        failedTypes);

                typeParameters.add(typeParameterTypeDeclaration);
            } catch (UApiSchemaParseError e2) {
                parseFailures.addAll(e2.schemaParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new UTypeDeclaration(type, nullable, typeParameters);
    }
}
