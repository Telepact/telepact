package io.github.telepact.internal.schema;

import java.util.List;
import java.util.Map;
import java.util.TreeMap;

public class MapSchemaParseFailuresToPseudoJson {
    public static List<Object> mapSchemaParseFailuresToPseudoJson(
            List<SchemaParseFailure> schemaParseFailures, Map<String, String> documentNamesToJson) {
        return (List<Object>) schemaParseFailures.stream()
                .map(f -> (Object) new TreeMap<>() {
                    {
                        put("document", f.documentName);
                        put("location", GetPathDocumentCoordinatesPseudoJson
                                .getPathDocumentCoordinatesPseudoJson(f.path, documentNamesToJson.get(f.documentName)));
                        put("path", f.path);
                        put("reason", Map.of(f.reason, f.data));
                    }
                })
                .toList();
    }
}
