package uapi.internal.schema;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

public class OffsetSchemaIndex {
    public static List<SchemaParseFailure> offsetSchemaIndex(List<SchemaParseFailure> initialFailures,
            String documentName) {
        var finalList = new ArrayList<SchemaParseFailure>();

        for (var failure : initialFailures) {
            var reason = failure.reason;
            var path = failure.path;
            var data = (Map<String, Object>) failure.data;
            var newPath = new ArrayList<>(path);

            finalList.add(new SchemaParseFailure(newPath, reason, data, documentName));
        }

        return finalList;
    }
}
