package uapi.internal.schema;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

import uapi.UApiSchemaParseError;
import uapi.internal.types.UError;
import uapi.internal.types.UFn;
import uapi.internal.types.UStruct;
import uapi.internal.types.UType;
import uapi.internal.types.UUnion;

public class ApplyErrorToParsedTypes {
    static void applyErrorToParsedTypes(int errorIndex, UError error, Map<String, UType> parsedTypes,
            Map<String, Integer> schemaKeysToIndex) {
        var parseFailures = new ArrayList<SchemaParseFailure>();
        for (var parsedType : parsedTypes.entrySet()) {
            UFn f;
            try {
                f = (UFn) parsedType.getValue();
            } catch (ClassCastException e) {
                continue;
            }

            String fnName = f.name;

            var regex = Pattern.compile(f.errorsRegex);

            UUnion fnResult = f.result;
            Map<String, UStruct> fnResultCases = fnResult.cases;
            UUnion errorErrors = error.errors;
            Map<String, UStruct> errorCases = errorErrors.cases;

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
                    parseFailures.add(new SchemaParseFailure(List.of(errorIndex, "errors", errorCaseIndex, newKey),
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
