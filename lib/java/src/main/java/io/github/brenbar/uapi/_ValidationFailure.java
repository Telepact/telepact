package io.github.brenbar.uapi;

import java.util.List;
import java.util.Map;

class _ValidationFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public _ValidationFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}