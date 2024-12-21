package uapi.internal.schema;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import uapi.UApiSchemaParseError;

public class CatchErrorCollisions {
    public static void catchErrorCollisions(Map<String, List<Object>> uApiSchemaNameToPseudoJson, Set<String> errorKeys,
            Map<String, Integer> keysToIndex, Map<String, String> schemaKeysToDocumentName) {
        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        var errorKeysList = new ArrayList<>(errorKeys);

        errorKeysList.sort((k1, k2) -> {
            var index1 = keysToIndex.get(k1);
            var index2 = keysToIndex.get(k2);
            return index1 - index2;
        });

        for (var i = 0; i < errorKeysList.size(); i++) {
            for (var j = i + 1; j < errorKeysList.size(); j++) {
                var defKey = errorKeysList.get(i);
                var otherDefKey = errorKeysList.get(j);

                int index = keysToIndex.get(defKey);
                int otherIndex = keysToIndex.get(otherDefKey);

                var documentName = schemaKeysToDocumentName.get(defKey);
                var otherDocumentName = schemaKeysToDocumentName.get(otherDefKey);

                var uApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(documentName);
                var otherUApiSchemaPseudoJson = uApiSchemaNameToPseudoJson.get(otherDocumentName);

                var def = (Map<String, Object>) uApiSchemaPseudoJson.get(index);
                var otherDef = (Map<String, Object>) otherUApiSchemaPseudoJson.get(otherIndex);

                var errDef = (List<Object>) def.get(defKey);
                var otherErrDef = (List<Object>) otherDef.get(otherDefKey);

                for (int k = 0; k < errDef.size(); k++) {
                    var thisErrDef = (Map<String, Object>) errDef.get(k);
                    var thisErrDefKeys = new HashSet<>(thisErrDef.keySet());
                    thisErrDefKeys.remove("///");

                    for (int l = 0; l < otherErrDef.size(); l++) {
                        var thisOtherErrDef = (Map<String, Object>) otherErrDef.get(l);
                        var thisOtherErrDefKeys = new HashSet<>(thisOtherErrDef.keySet());
                        thisOtherErrDefKeys.remove("///");

                        if (thisErrDefKeys.equals(thisOtherErrDefKeys)) {
                            String thisErrorDefKey = thisErrDefKeys.iterator().next();
                            String thisOtherErrorDefKey = thisOtherErrDefKeys.iterator().next();
                            parseFailures.add(new SchemaParseFailure(
                                    otherDocumentName,
                                    List.of(otherIndex, otherDefKey, l, thisOtherErrorDefKey),
                                    "PathCollision",
                                    Map.of("document", documentName, "path",
                                            List.of(index, defKey, k, thisErrorDefKey))));
                        }
                    }
                }
            }
        }

        if (!parseFailures.isEmpty()) {
            throw new UApiSchemaParseError(parseFailures);
        }
    }
}
