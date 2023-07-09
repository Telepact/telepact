package io.github.brenbar.japi;

import java.util.Map;

class InternalJApiError extends RuntimeException {
    public final String target;
    public final Map<String, Object> headers;
    public final Map<String, Object> body;

    InternalJApiError(String target, Map<String, Object> headers, Map<String, Object> details) {
        super("%s: %s".formatted(target, details));
        this.target = target;
        this.headers = headers;
        this.body = details;
    }

    InternalJApiError(String target, Map<String, Object> headers, Map<String, Object> details, Throwable cause) {
        super("%s: %s".formatted(target, details), cause);
        this.target = target;
        this.headers = headers;
        this.body = details;
    }
}
