package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaErrorUtil {

    static void applyErrorToParsedTypes(_UError error, Map<String, _UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
        String errorName = error.name;
        var errorIndex = schemaKeysToIndex.get(errorName);

        var parseFailures = new ArrayList<_SchemaParseFailure>();
        for (var parsedType : parsedTypes.entrySet()) {
            _UFn f;
            try {
                f = (_UFn) parsedType.getValue();
            } catch (ClassCastException e) {
                continue;
            }

            String fnName = f.name;

            var regex = Pattern.compile(f.errorsRegex);
            var matcher = regex.matcher(errorName);
            if (!matcher.find()) {
                continue;
            }

            _UUnion fnResult = f.result;
            Map<String, _UStruct> fnResultCases = fnResult.cases;
            _UUnion errorFnResult = error.errors;
            Map<String, _UStruct> errorFnResultCases = errorFnResult.cases;

            if (fnName.startsWith("fn._")) {
                // Only internal errors can change internal functions
                if (!errorName.startsWith("error._")) {
                    continue;
                }
            }

            for (var errorResultField : errorFnResultCases.entrySet()) {
                var newKey = errorResultField.getKey();
                if (fnResultCases.containsKey(newKey)) {
                    var otherPathIndex = schemaKeysToIndex.get(fnName);
                    parseFailures.add(new _SchemaParseFailure(List.of(errorIndex, errorName, "->", newKey),
                            "PathCollision", Map.of("other", List.of(otherPathIndex, "->", newKey))));
                }
                fnResultCases.put(newKey, errorResultField.getValue());
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }

    public static _UError parseErrorType(Map<String, Object> errorDefinitionAsParsedJson, String schemaKey,
            List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<_SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var index = schemaKeysToIndex.get(schemaKey);
        final List<Object> basePath = List.of(index);

        final var parseFailures = new ArrayList<_SchemaParseFailure>();

        final var otherKeys = new HashSet<>(errorDefinitionAsParsedJson.keySet());

        otherKeys.remove(schemaKey);
        otherKeys.remove("///");

        if (otherKeys.size() > 0) {
            for (final var k : otherKeys) {
                final List<Object> loopPath = _ValidateUtil.append(basePath, k);

                parseFailures.add(new _SchemaParseFailure(loopPath, "ObjectKeyDisallowed", Map.of()));
            }
        }

        final var defInit = errorDefinitionAsParsedJson.get(schemaKey);
        final List<Object> thisPath = _ValidateUtil.append(basePath, schemaKey);

        final Map<String, Object> def;
        try {
            def = _CastUtil.asMap(defInit);
        } catch (ClassCastException e) {
            final List<_SchemaParseFailure> thisParseFailures = _ParseSchemaUtil
                    .getTypeUnexpectedValidationFailure(thisPath, defInit, "Object");

            parseFailures.addAll(thisParseFailures);
            throw new UApiSchemaParseError(parseFailures);
        }

        final var resultSchemaKey = "->";
        final var okCaseRequired = false;
        final var typeParameterCount = 0;
        final List<Object> errorPath = _ValidateUtil.append(thisPath, resultSchemaKey);

        if (!def.containsKey(resultSchemaKey)) {
            parseFailures.add(new _SchemaParseFailure(errorPath, "RequiredObjectKeyMissing", Map.of()));
        }

        if (parseFailures.size() > 0) {
            throw new UApiSchemaParseError(parseFailures);
        }

        final _UUnion error = _ParseSchemaCustomTypeUtil.parseUnionType(thisPath, def, resultSchemaKey, okCaseRequired,
                typeParameterCount, uApiSchemaPseudoJson, schemaKeysToIndex, parsedTypes, typeExtensions,
                allParseFailures, failedTypes);

        return new _UError(schemaKey, error);
    }
}
