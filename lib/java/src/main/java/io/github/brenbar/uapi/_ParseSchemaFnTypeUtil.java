package io.github.brenbar.uapi;

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
            List<Object> originalUApiSchema,
            Map<String, Integer> schemaKeysToIndex,
            Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions,
            List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var parseFailures = new ArrayList<SchemaParseFailure>();
        final var typeParameterCount = 0;

        _UUnion callType = null;
        try {
            final var argType = _ParseSchemaCustomTypeUtil.parseStructType(path, functionDefinitionAsParsedJson,
                    schemaKey, typeParameterCount, originalUApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions,
                    allParseFailures, failedTypes);
            callType = new _UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);
        } catch (UApiSchemaParseError e) {
            parseFailures.addAll(e.schemaParseFailures);
        }

        var resPath = _ValidateUtil.append(path, "->");

        _UUnion resultType = null;
        if (!functionDefinitionAsParsedJson.containsKey("->")) {
            parseFailures.add(new SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of()));
        } else {
            try {
                resultType = _ParseSchemaCustomTypeUtil.parseUnionType(path, functionDefinitionAsParsedJson, "->",
                        true, typeParameterCount, originalUApiSchema, schemaKeysToIndex, parsedTypes,
                        typeExtensions,
                        allParseFailures, failedTypes);
            } catch (UApiSchemaParseError e) {
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
            throw new UApiSchemaParseError(parseFailures);
        }

        var type = new _UFn(schemaKey, callType, resultType, extendsRegex);

        return type;
    }
}
