package io.github.brenbar.japi;

import java.util.ArrayList;
import java.util.HashMap;
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
        var argType = _ParseSchemaCustomTypeUtil.parseStructType(path, functionDefinitionAsParsedJson, schemaKey, 0,
                originalJApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions, allParseFailures, failedTypes);
        var callType = new UUnion(schemaKey, Map.of(schemaKey, argType), typeParameterCount);

        var resPath = _ValidateUtil.append(path, "->");

        if (!functionDefinitionAsParsedJson.containsKey("->")) {
            parseFailures.add(new SchemaParseFailure(resPath, "RequiredObjectKeyMissing", Map.of()));
            throw new JApiSchemaParseError(parseFailures);
        }

        var resultType = _ParseSchemaCustomTypeUtil.parseUnionType(path, functionDefinitionAsParsedJson, "->",
                !isForTrait, 0, originalJApiSchema, schemaKeysToIndex, parsedTypes, typeExtensions,
                allParseFailures, failedTypes);

        if (!parseFailures.isEmpty()) {
            throw new JApiSchemaParseError(parseFailures);
        }

        var type = new UFn(schemaKey, callType, resultType);

        return type;
    }
}
