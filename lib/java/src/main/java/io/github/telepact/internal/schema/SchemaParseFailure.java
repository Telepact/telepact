package io.github.telepact.internal.schema;

import java.util.List;
import java.util.Map;

public class SchemaParseFailure {
    public final String documentName;
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public SchemaParseFailure(String documentName, List<Object> path, String reason, Map<String, Object> data) {
        this.documentName = documentName;
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}
