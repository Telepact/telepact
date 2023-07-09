package io.github.brenbar.japi;

import java.util.Map;

/**
 * A jAPI error.
 * 
 * Server implementations can use this class to produce custom server-side
 * errors in accordance with their jAPI Schema.
 * 
 */
public class JApiError extends RuntimeException {

    public final String target;
    public final Map<String, Object> body;

    public JApiError(String target, Map<String, Object> body) {
        super("%s: %s".formatted(target, body));
        this.target = target;
        this.body = body;
    }

    public JApiError(String target, Map<String, Object> body, Throwable cause) {
        super("%s: %s".formatted(target, body), cause);
        this.target = target;
        this.body = body;
    }
}
