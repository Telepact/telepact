package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

import static io.github.brenbar.uapi.internal.GetType.getType;

public class GetTypeUnexpectedValidationFailure {
        static List<ValidationFailure> getTypeUnexpectedValidationFailure(List<Object> path, Object value,
                        String expectedType) {
                final var actualType = getType(value);
                final Map<String, Object> data = new TreeMap<>(
                                Map.ofEntries(Map.entry("actual", Map.of(actualType, Map.of())),
                                                Map.entry("expected", Map.of(expectedType, Map.of()))));
                return List.of(
                                new ValidationFailure(path, "TypeUnexpected", data));
        }
}
