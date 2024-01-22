package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

class _ParseSchemaFnTypeUtil {

    static _UFn parseFunctionType(List<Object> path, Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<_SchemaParseFailure>();
        final var typeParameterCount = 0;
        final var isForFn = true;

        _UUnion callType = null;
        try {
            final _UStruct argType = _ParseSchemaCustomTypeUtil.parseStructType(path, functionDefinitionAsParsedJson,
                    schemaKey, isForFn, typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes,
                    typeExtensions,
                    allParseFailures, failedTypes);
            callType = new _UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final var resultSchemaKey = "->";
        final List<Object> resPath = _Util.append(path, resultSchemaKey);

        _UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey(resultSchemaKey)) {
            parseFailures.add(new _SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of()));
        } else {
            try {
                resultType = _ParseSchemaCustomTypeUtil.parseUnionType(path, functionDefinitionAsParsedJson,
                        resultSchemaKey, isForFn, typeParameterCount, uApiSchemaPseudoJson,
                        schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        final var errorsRegexKey = "errors";
        final var regexPath = _Util.append(path, errorsRegexKey);

        String errorsRegex = null;
        if (functionDefinitionAsParsedJson.containsKey(errorsRegexKey) && !schemaKey.startsWith("fn._")) {
            parseFailures.add(new _SchemaParseFailure(regexPath, "ObjectKeyDisallowed", Map.of()));
        } else {
            final Object errorsRegexInit = functionDefinitionAsParsedJson.getOrDefault(errorsRegexKey,
                    "^error\\..*$");
            try {
                errorsRegex = _CastUtil.asString(errorsRegexInit);
            } catch (ClassCastException e) {
                final List<_SchemaParseFailure> thisParseFailures = _ParseSchemaToolUtil
                        .getTypeUnexpectedValidationFailure(
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
