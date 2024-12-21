package uapi.internal.schema;

import java.util.Objects;
import java.util.Set;

public class FindMatchingSchemaKey {
    public static String findMatchingSchemaKey(Set<String> schemaKeys, String schemaKey) {
        for (final var k : schemaKeys) {
            if (schemaKey.startsWith("info.") && k.startsWith("info.")) {
                return k;
            }
            if (Objects.equals(k, schemaKey)) {
                return k;
            }
        }
        return null;
    }
}
