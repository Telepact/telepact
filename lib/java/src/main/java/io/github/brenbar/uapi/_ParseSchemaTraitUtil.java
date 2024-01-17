package io.github.brenbar.uapi;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Pattern;

class _ParseSchemaErrorUtil {

    static void applyErrorToParsedTypes(UError error, Map<String, _UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
        String errorName = error.name;
        var errorIndex = schemaKeysToIndex.get(errorName);

        var parseFailures = new ArrayList<SchemaParseFailure>();
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
                    parseFailures.add(new SchemaParseFailure(List.of(errorIndex, errorName, "->", newKey),
                            "PathCollision", Map.of("other", List.of(otherPathIndex, "->", newKey))));
                }
                fnResultCases.put(newKey, errorResultField.getValue());
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }

    public static UError parseErrorType(Map<String, Object> errorDefinitionAsParsedJson, String schemaKey,
            List<Object> uApiSchemaPseudoJson, Map<String, Integer> schemaKeysToIndex, Map<String, _UType> parsedTypes,
            Map<String, _UType> typeExtensions, List<SchemaParseFailure> allParseFailures, Set<String> failedTypes) {
        final var defInit = errorDefinitionAsParsedJson.get(schemaKey);
        final var index = schemaKeysToIndex.get(schemaKey);
        final List<Object> thisPath = List.of(index, schemaKey);

        final Map<String, Object> def;
        try {
            def = _CastUtil.asMap(defInit);
        } catch (ClassCastException e) {
            final List<SchemaParseFailure> thisParseFailures = _ParseSchemaUtil
                    .getTypeUnexpectedValidationFailure(thisPath, defInit, "Object");
            throw new UApiSchemaParseError(thisParseFailures);
        }

        final var resultSchemaKey = "->";
        final var okCaseRequired = false;
        final List<Object> errorPath = _ValidateUtil.append(thisPath, resultSchemaKey);

        if (!def.containsKey(resultSchemaKey)) {
            throw new UApiSchemaParseError(
                    List.of(new SchemaParseFailure(errorPath, "RequiredObjectKeyMissing", Map.of())));
        }

        final _UUnion error = _ParseSchemaCustomTypeUtil.parseUnionType(thisPath, def, resultSchemaKey,
                okCaseRequired, 0, uApiSchemaPseudoJson,
                schemaKeysToIndex, parsedTypes,
                typeExtensions,
                allParseFailures, failedTypes);

        return new UError(schemaKey, error);
    }
}
