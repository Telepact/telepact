package uapi.internal.schema;

import static uapi.internal.types.GetType.getType;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class GetTypeUnexpectedParseFailure {
        public static List<SchemaParseFailure> getTypeUnexpectedParseFailure(String documentName, List<Object> path,
                        Object value,
                        String expectedType) {
                final var actualType = getType(value);
                final Map<String, Object> data = new TreeMap<>(
                                Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                                                Map.entry("expected", Map.of(expectedType, Map.of()))));
                return List.of(
                                new SchemaParseFailure(documentName, path, "TypeUnexpected", data));
        }
}
