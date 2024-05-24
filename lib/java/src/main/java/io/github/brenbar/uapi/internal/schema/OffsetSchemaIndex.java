package io.github.brenbar.uapi.internal.schema;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

public class OffsetSchemaIndex {
    public static List<SchemaParseFailure> offsetSchemaIndex(List<SchemaParseFailure> initialFailures, int offset,
            Map<String, Integer> schemaKeysToIndex, Set<Integer> errorIndices) {
        final var finalList = new ArrayList<SchemaParseFailure>();

        final var indexToSchemaKey = schemaKeysToIndex.entrySet().stream()
                .collect(Collectors.toMap(e -> e.getValue(), e -> e.getKey()));

        for (final var f : initialFailures) {
            final String reason = f.reason;
            final List<Object> path = f.path;
            final Map<String, Object> data = f.data;
            final var newPath = new ArrayList<>(path);

            final var originalIndex = (Integer) newPath.get(0);
            newPath.set(0, originalIndex - offset);

            final Map<String, Object> finalData;
            if (reason.equals("PathCollision")) {
                final var otherNewPath = new ArrayList<>((List<Object>) data.get("other"));

                otherNewPath.set(0, (Integer) otherNewPath.get(0) - offset);
                finalData = Map.of("other", otherNewPath);
            } else {
                finalData = data;
            }

            String schemaKey;
            if (errorIndices.contains(originalIndex)) {
                schemaKey = "errors";
            } else {
                schemaKey = indexToSchemaKey.get(originalIndex);
            }

            finalList.add(new SchemaParseFailure(newPath, reason, finalData, schemaKey));
        }

        return finalList;
    }
}
