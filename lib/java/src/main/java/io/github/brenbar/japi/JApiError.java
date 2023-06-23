package io.github.brenbar.japi;

import java.util.Map;

public class JApiError extends RuntimeException {
    public final String target;
    public final Map<String, Object> details;

    public JApiError(String target, Map<String, Object> details) {
        super("%s: %s".formatted(target, details));
        this.target = target;
        this.details = details;
    }

    public JApiError(String target, Map<String, Object> details, Throwable cause) {
        super(cause);
        this.target = target;
        this.details = details;
    }
}
