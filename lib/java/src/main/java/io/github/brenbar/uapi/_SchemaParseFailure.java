package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;

class _SchemaParseFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public _SchemaParseFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}
