package uapi.internal.schema;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;
import uapi.internal.types.UError;
import uapi.internal.types.UFn;
import uapi.internal.types.UType;
import uapi.UApiSchemaParseError;

public class ApplyErrorToParsedTypes {
    public static void applyErrorToParsedTypes(UError error,
            Map<String, UType> parsedTypes, Map<String, String> schemaKeysToDocumentNames,
            Map<String, Integer> schemaKeysToIndex, Map<String, String> documentNamesToJson) {
        var parseFailures = new ArrayList<SchemaParseFailure>();

        var errorKey = error.name;
        var errorIndex = schemaKeysToIndex.get(errorKey);
        var documentName = schemaKeysToDocumentNames.get(errorKey);

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

            var matcher = regex.matcher(errorKey);
            if (!matcher.matches()) {
                continue;
            }

            for (var errorCaseEntry : errorCases.entrySet()) {
                var errorCaseName = errorCaseEntry.getKey();
                var errorCase = errorCaseEntry.getValue();
                var newKey = errorCaseName;

                if (fnResultCases.containsKey(newKey)) {
                    var otherPathIndex = schemaKeysToIndex.get(fnName);
                    var errorCaseIndex = error.errors.caseIndices.get(newKey);
                    var otherDocumentName = schemaKeysToDocumentNames.get(fnName);
                    var fnErrorCaseIndex = f.result.caseIndices.get(newKey);
                    List<Object> otherFinalPath = List.of(otherPathIndex, "->", fnErrorCaseIndex, newKey);
                    var otherDocumentJson = documentNamesToJson.get(otherDocumentName);
                    var otherLocationPseudoJson = GetPathDocumentCoordinatesPseudoJson
                            .getPathDocumentCoordinatesPseudoJson(
                                    otherFinalPath, otherDocumentJson);
                    parseFailures.add(new SchemaParseFailure(documentName,
                            List.of(errorIndex, errorKey, errorCaseIndex, newKey),
                            "PathCollision",
                            Map.of("document", otherDocumentName, "path",
                                    otherFinalPath, "location", otherLocationPseudoJson)));
                }
                fnResultCases.put(newKey, errorCase);
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures, documentNamesToJson);
        }
    }
}
