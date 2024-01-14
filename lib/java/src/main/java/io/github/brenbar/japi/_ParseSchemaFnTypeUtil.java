package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

class _ParseSchemaFnTypeUtil {

    private static final _ParseSchemaFnTypeUtil INST = new _ParseSchemaFnTypeUtil();

    static _UFn parseFunctionType(
            List<Object> path,
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        var parseFailures = new ArrayList<SchemaParseFailure>();

        var typeParameterCount = 0;

        _UUnion callType = null;
        try {
            var argType = _ParseSchemaCustomTypeUtil.parseStructType(path, functionDefinitionAsParsedJson, schemaKey,
                    typeParameterCount,
                    originalJApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
            callType = new _UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);
        } catch (JApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        var resPath = _ValidateUtil.append(path, "->");

        _UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey("->")) {
            parseFailures.add(new SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of()));
        } else {
            try {
                resultType = _ParseSchemaCustomTypeUtil.parseUnionType(path, functionDefinitionAsParsedJson, "->",
                        true, typeParameterCount, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                        typeExtensions,
                        allParseFailures, failedTypes);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        var regexPath = _ValidateUtil.append(path, "extends");

        String extendsRegex = null;
        if (functionDefinitionAsParsedJson.containsKey("extends") && !schemaKey.startsWith("fn._")) {
            parseFailures.add(new SchemaParseFailure(regexPath, "ObjectKeyDisallowed", Map.of()));
        } else {
            Object extendsRegexInit = functionDefinitionAsParsedJson.getOrDefault("extends", "^trait\\..*$");
            try {
                extendsRegex = _CastUtil.asString(extendsRegexInit);
            } catch (ClassCastException e) {
                parseFailures
                        .addAll(_ParseSchemaUtil.getTypeUnexpectedValidationFailure(regexPath, extendsRegexInit,
                                "String"));
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new _UFn(schemaKey, callType, resultType, extendsRegex);

        return type;
    }
}
