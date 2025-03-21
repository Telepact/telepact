package io.github.telepact.internal.validation;

import java.util.List;
import java.util.Map;

public class ValidationFailure {
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public ValidationFailure(List<Object> path, String reason, Map<String, Object> data) {
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}
