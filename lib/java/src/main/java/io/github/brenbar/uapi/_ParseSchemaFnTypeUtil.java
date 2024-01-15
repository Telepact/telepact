package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

class _ParseSchemaFnTypeUtil {

    static _UFn parseFunctionType(List<Object> path, Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey, List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes, Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var typeParameterCount = 0;

        _UUnion callType = null;
        try {
            final _UStruct argType = _ParseSchemaCustomTypeUtil.parseStructType(path, functionDefinitionAsParsedJson,
                    schemaKey, typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions,
                    allParseFailures, failedTypes);
            callType = new _UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        final var resultSchemaKey = "->";
        final var okCaseRequired = true;
        final List<Object> resPath = _ValidateUtil.append(path, resultSchemaKey);

        _UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey(resultSchemaKey)) {
            parseFailures.add(new SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of()));
        } else {
            try {
                resultType = _ParseSchemaCustomTypeUtil.parseUnionType(path, functionDefinitionAsParsedJson,
                        resultSchemaKey, okCaseRequired, typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex,
                        parsedTypes, typeExtensions, allParseFailures, failedTypes);
            } catch (UApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        final var extendsRegexKey = "extends";
        final var regexPath = _ValidateUtil.append(path, extendsRegexKey);

        String extendsRegex = null;
        if (functionDefinitionAsParsedJson.containsKey(extendsRegexKey) && !schemaKey.startsWith("fn._")) {
            parseFailures.add(new SchemaParseFailure(regexPath, "ObjectKeyDisallowed", Map.of()));
        } else {
            final Object extendsRegexInit = functionDefinitionAsParsedJson.getOrDefault(extendsRegexKey,
                    "^trait\\..*$");
            try {
                extendsRegex = _CastUtil.asString(extendsRegexInit);
            } catch (ClassCastException e) {
                final List<SchemaParseFailure> thisParseFailures = _ParseSchemaUtil.getTypeUnexpectedValidationFailure(
                        regexPath, extendsRegexInit, "String");

                parseFailures
                        .addAll(thisParseFailures);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }

        return new _UFn(schemaKey, callType, resultType, extendsRegex);
    }
}
