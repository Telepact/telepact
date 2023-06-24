package io.github.brenbar.japi;

import java.util.Map;

public class JApiError extends RuntimeException {
    public final String target;
    public final Map<String, Object> body;

    public JApiError(String target, Map<String, Object> details) {
        super("%s: %s".formatted(target, details));
        this.target = target;
        this.body = details;
    }

    public JApiError(String target, Map<String, Object> details, Throwable cause) {
        super("%s: %s".formatted(target, details), cause);
        this.target = target;
        this.body = details;
    }
}
