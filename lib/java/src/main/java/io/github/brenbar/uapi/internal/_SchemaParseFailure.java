package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;

public class _SchemaParseFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;
    public final String key;

    public _SchemaParseFailure(List<Object> path, String reason, Map<String, Object> data, String key) {
        this.path = path;
        this.reason = reason;
        this.data = data;
        this.key = key;
    }
}
