package uapi.internal.schema;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import uapi.UApiSchemaParseError;
import uapi.internal.schema.SchemaParseFailure;

public class CatchErrorCollisions {
    public static void catchErrorCollisions(List<Object> uApiSchemaPseudoJson, Set<String> errorKeys,
            Map<String, Integer> keysToIndex) {
        List<SchemaParseFailure> parseFailures = new ArrayList<>();

        List<Integer> indices = new ArrayList<>();
        for (String key : errorKeys) {
            indices.add(keysToIndex.get(key));
        }
        indices.sort(Integer::compareTo);

        Map<Integer, String> indexToKeys = new HashMap<>();
        for (Map.Entry<String, Integer> entry : keysToIndex.entrySet()) {
            indexToKeys.put(entry.getValue(), entry.getKey());
        }

        for (int i = 0; i < indices.size(); i++) {
            for (int j = i + 1; j < indices.size(); j++) {
                int index = indices.get(i);
                int otherIndex = indices.get(j);

                var def = (Map<String, Object>) uApiSchemaPseudoJson.get(index);
                var otherDef = (Map<String, Object>) uApiSchemaPseudoJson.get(otherIndex);

                String defKey = indexToKeys.get(index);
                String otherDefKey = indexToKeys.get(otherIndex);

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
                                    List.of(otherIndex, otherDefKey, l, thisOtherErrorDefKey),
                                    "PathCollision",
                                    Map.of("other", List.of(index, defKey, k, thisErrorDefKey)),
                                    otherDefKey));
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
