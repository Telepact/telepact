package uapi.internal.schema;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import uapi.internal.schema.SchemaParseFailure;
import uapi.internal.types.UError;
import uapi.internal.types.UFn;
import uapi.internal.types.UType;
import uapi.internal.types.UUnion;
import uapi.UApiSchemaParseError;

public class ApplyErrorToParsedTypes {
    public static void applyErrorToParsedTypes(String errorKey, int errorIndex, UError error,
            Map<String, UType> parsedTypes, Map<String, Integer> schemaKeysToIndex) {
        var parseFailures = new ArrayList<SchemaParseFailure>();

        for (var entry : parsedTypes.entrySet()) {
            var parsedTypeName = entry.getKey();
            var parsedType = entry.getValue();

            if (!(parsedType instanceof UFn)) {
                continue;
            }

            var f = (UFn) parsedType;
            var fnName = f.name;
            var regex = Pattern.compile(f.errorsRegex);
            var fnResult = f.result;
            var fnResultCases = fnResult.cases;
            var errorErrors = error.errors;
            var errorCases = errorErrors.cases;

            for (var errorCaseEntry : errorCases.entrySet()) {
                var errorCaseName = errorCaseEntry.getKey();
                var errorCase = errorCaseEntry.getValue();
                var newKey = errorCaseName;

                var matcher = regex.matcher(newKey);
                if (!matcher.matches()) {
                    continue;
                }

                if (fnResultCases.containsKey(newKey)) {
                    var otherPathIndex = schemaKeysToIndex.get(fnName);
                    var errorCaseIndex = error.errors.caseIndices.get(newKey);
                    var fnErrorCaseIndex = f.result.caseIndices.get(newKey);
                    parseFailures.add(new SchemaParseFailure(
                            List.of(errorIndex, errorKey, errorCaseIndex, newKey),
                            "PathCollision",
                            Map.of("other", List.of(otherPathIndex, "->", fnErrorCaseIndex, newKey)),
                            null));
                }
                fnResultCases.put(newKey, errorCase);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }
}
