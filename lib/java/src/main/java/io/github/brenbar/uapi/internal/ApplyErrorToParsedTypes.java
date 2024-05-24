package io.github.brenbar.uapi.internal;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import io.github.brenbar.uapi.UApiSchemaParseError;

public class ApplyErrorToParsedTypes {
    static void applyErrorToParsedTypes(int errorIndex, _UError error, Map<String, _UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
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

            _UUnion fnResult = f.result;
            Map<String, _UStruct> fnResultCases = fnResult.cases;
            _UUnion errorErrors = error.errors;
            Map<String, _UStruct> errorCases = errorErrors.cases;

            for (var errorCase : errorCases.entrySet()) {
                var newKey = errorCase.getKey();

                var matcher = regex.matcher(newKey);
                if (!matcher.find()) {
                    continue;
                }

                if (fnResultCases.containsKey(newKey)) {
                    final var otherPathIndex = schemaKeysToIndex.get(fnName);
                    final var errorCaseIndex = error.errors.caseIndices.get(newKey);
                    final var fnErrorCaseIndex = f.result.caseIndices.get(newKey);
                    parseFailures.add(new _SchemaParseFailure(List.of(errorIndex, "errors", errorCaseIndex, newKey),
                            "PathCollision", Map.of("other", List.of(otherPathIndex, "->", fnErrorCaseIndex, newKey)),
                            null));
                }
                fnResultCases.put(newKey, errorCase.getValue());
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }
}
