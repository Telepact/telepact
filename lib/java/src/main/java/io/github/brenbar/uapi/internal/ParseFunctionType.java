package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import io.github.brenbar.uapi.UApiSchemaParseError;

import static io.github.brenbar.uapi.internal.ParseStructType.parseStructType;
import static io.github.brenbar.uapi.internal.ParseUnionType.parseUnionType;
import static io.github.brenbar.uapi.internal.Append.append;
import static io.github.brenbar.uapi.internal.AsString.asString;
import static io.github.brenbar.uapi.internal.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;

public class ParseFunctionType {

    static _UFn parseFunctionType(List<Object> path, Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var typeParameterCount = 0;

        _UUnion callType = null;
        try {
            final _UStruct argType = parseStructType(path, functionDefinitionAsParsedJson,
                    schemaKey, List.of("->", "_errors"), typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex,
                    parsedTypes,
                    typeExtensions,
                    allParseFailures, failedTypes);
            callType = new _UUnion(schemaKey, Map.of(schemaKey, argType), Map.of(schemaKey, 0), typeParameterCount);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final var resultSchemaKey = "->";
        final List<Object> resPath = append(path, resultSchemaKey);

        _UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey(resultSchemaKey)) {
            parseFailures.add(new _SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of(), null));
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
            parseFailures.add(new _SchemaParseFailure(regexPath, "ObjectKeyDisallowed", Map.of(), null));
        } else {
            final Object errorsRegexInit = functionDefinitionAsParsedJson.getOrDefault(errorsRegexKey,
                    "^.*$");
            try {
                errorsRegex = asString(errorsRegexInit);
            } catch (ClassCastException e) {
                final List<_SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(
                        regexPath, errorsRegexInit, "String");

                parseFailures
                        .addAll(thisParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new _UFn(schemaKey, callType, resultType, errorsRegex);
    }

}
