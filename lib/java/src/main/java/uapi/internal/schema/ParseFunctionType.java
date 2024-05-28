package uapi.internal.schema;

import static uapi.internal.schema.GetTypeUnexpectedParseFailure.getTypeUnexpectedParseFailure;
import static uapi.internal.schema.ParseStructType.parseStructType;
import static uapi.internal.schema.ParseUnionType.parseUnionType;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UFn;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;
import uapi.internal.types.UUnion;

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

        final List<Object> resPath = new ArrayList<>(path);
        resPath.add(resultSchemaKey);

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

        final var regexPath = new ArrayList<>(path);
        regexPath.add(errorsRegexKey);

        String errorsRegex = null;
        if (functionDefinitionAsParsedJson.containsKey(errorsRegexKey) && !schemaKey.endsWith("_")) {
            parseFailures.add(new SchemaParseFailure(regexPath, "ObjectKeyDisallowed", Map.of(), null));
        } else {
            final Object errorsRegexInit = functionDefinitionAsParsedJson.getOrDefault(errorsRegexKey,
                    "^.*$");

            if (!(errorsRegexInit instanceof String)) {
                final List<SchemaParseFailure> thisParseFailures = getTypeUnexpectedParseFailure(
                        regexPath, errorsRegexInit, "String");

                parseFailures
                        .addAll(thisParseFailures);
            } else {
                errorsRegex = (String) errorsRegexInit;
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new UFn(schemaKey, callType, resultType, errorsRegex);
    }

}
