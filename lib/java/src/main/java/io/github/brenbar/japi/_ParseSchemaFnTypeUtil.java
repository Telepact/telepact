package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;

class _ParseSchemaFnTypeUtil {

    private static final _ParseSchemaFnTypeUtil INST = new _ParseSchemaFnTypeUtil();

    static UFn parseFunctionType(
            List<Object> path,
            Map<String, Object> functionDefinitionAsParsedJson,
            String schemaKey,
            List<Object> originalJApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, UType> parsedTypes,
            Map<String, TypeExtension> typeExtensions,
            boolean isForTrait, List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        var parseFailures = new ArrayList<SchemaParseFailure>();

        var typeParameterCount = 0;

        UUnion callType = null;
        try {
            var argType = _ParseSchemaCustomTypeUtil.parseStructType(path, functionDefinitionAsParsedJson, schemaKey,
                    typeParameterCount,
                    originalJApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
            callType = new UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);
        } catch (JApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        var resPath = _ValidateUtil.append(path, "->");

        UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey("->")) {
            parseFailures.add(new SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of()));
        } else {
            try {
                resultType = _ParseSchemaCustomTypeUtil.parseUnionType(path, functionDefinitionAsParsedJson, "->",
                        !isForTrait, typeParameterCount, originalJApiSchema, schemaKeysToIndex, parsedTypes,
                        typeExtensions,
                        allParseFailures, failedTypes);
            } catch (JApiSchemaParseError e) {
                parseFailures.addAll(e.schemaParseFailures);
            }
        }

        Object extendsRegexInit = functionDefinitionAsParsedJson.getOrDefault("extends", "^trait\\..*$");
        String extendsRegex = null;
        try {
            extendsRegex = _CastUtil.asString(extendsRegexInit);
        } catch (ClassCastException e) {
            var regexPath = _ValidateUtil.append(path, "extends");
            parseFailures
                    .addAll(_ParseSchemaUtil.getTypeUnexpectedValidationFailure(regexPath, extendsRegexInit, "String"));
        }

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new UFn(schemaKey, callType, resultType, extendsRegex);

        return type;
    }
}
