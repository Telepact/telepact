package io.github.brenbar.uapi.internal.schema;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;
import io.github.brenbar.uapi.internal.types.UFn;
import io.github.brenbar.uapi.internal.types.UStruct;
import io.github.brenbar.uapi.internal.types.UType;
import io.github.brenbar.uapi.internal.types.UUnion;

import static io.github.brenbar.uapi.internal.Append.append;
import static io.github.brenbar.uapi.internal.AsString.asString;
import static io.github.brenbar.uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static io.github.brenbar.uapi.internal.schema.ParseStructType.parseStructType;
import static io.github.brenbar.uapi.internal.schema.ParseUnionType.parseUnionType;

public class ParseFunctionType {

    static UFn parseFunctionType(List<Object> path, Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes, Map<String, UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var typeParameterCount = 0;

        UUnion callType = null;
        try {
            final UStruct argType = parseStructType(path, functionDefinitionAsParsedJson,
                    schemaKey, List.of("->", "_errors"), typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions,
                    allParseFailures, failedTypes);
            callType = new UUnion(schemaKey, Map.of(schemaKey, argType), Map.of(schemaKey, 0), typeParameterCount);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final var resultSchemaKey = "->";
        final List<Object> resPath = append(path, resultSchemaKey);

        UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey(resultSchemaKey)) {
            parseFailures.add(new SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of(), null));
        } else {
            try {
                resultType = parseUnionType(path, functionDefinitionAsParsedJson,
                        resultSchemaKey, functionDefinitionAsParsedJson.keySet().stream().toList(), List.of("Ok_"),
                        typeParameterCount, uApiSchemaPseudoJson,
                        schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        final var errorsRegexKey = "_errors";
        final var regexPath = append(path, errorsRegexKey);

        String errorsRegex = null;
        if (functionDefinitionAsParsedJson.containsKey(errorsRegexKey) && !schemaKey.endsWith("_")) {
            parseFailures.add(new SchemaParseFailure(regexPath, "ObjectKeyDisallowed", Map.of(), null));
        } else {
            final Object errorsRegexInit = functionDefinitionAsParsedJson.getOrDefault(errorsRegexKey,
                    "^.*$");
            try {
                errorsRegex = asString(errorsRegexInit);
            } catch (ClassCastException e) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(
                        regexPath, errorsRegexInit, "String");

                parseFailures
                        .addAll(thisParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new UFn(schemaKey, callType, resultType, errorsRegex);
    }

}
