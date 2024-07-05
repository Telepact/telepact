package uapi.internal.schema;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class OffsetSchemaIndex {
    public static List<SchemaParseFailure> offsetSchemaIndex(List<SchemaParseFailure> initialFailures, int offset,
            Map<String, Integer> schemaKeysToIndex) {
        var finalList = new ArrayList<SchemaParseFailure>();
        var indexToSchemaKey = new HashMap<Integer, String>();

        schemaKeysToIndex.forEach((key, value) -> indexToSchemaKey.put(value, key));

        for (var failure : initialFailures) {
            var reason = failure.reason;
            var path = failure.path;
            var data = (Map<String, Object>) failure.data;
            var newPath = new ArrayList<>(path);

            var originalIndex = (Integer) newPath.get(0);
            newPath.set(0, originalIndex - offset);

            Map<String, Object> finalData;
            if ("PathCollision".equals(reason)) {
                final var otherNewPath = new ArrayList<>((List<Object>) data.get("other"));
                otherNewPath.set(0, (Integer) otherNewPath.get(0) - offset);
                finalData = Map.of("other", otherNewPath);
            } else {
                finalData = data;
            }

            String schemaKey = indexToSchemaKey.get(originalIndex);

            finalList.add(new SchemaParseFailure(newPath, reason, finalData, schemaKey));
        }

        return finalList;
    }
}
