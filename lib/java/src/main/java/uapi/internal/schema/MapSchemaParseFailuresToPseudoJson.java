package uapi.internal.schema;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class MapSchemaParseFailuresToPseudoJson {
    public static List<Object> mapSchemaParseFailuresToPseudoJson(
            List<SchemaParseFailure> schemaParseFailures) {
        return (List<Object>) schemaParseFailures.stream()
                .map(f -> (Object) new TreeMap<>() {
                    {
                        put("document", f.documentName);
                        put("path", f.path);
                        put("reason", Map.of(f.reason, f.data));
                    }
                })
                .toList();
    }
}
