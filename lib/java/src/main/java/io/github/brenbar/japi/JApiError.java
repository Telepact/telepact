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
    public final Map<String, Object> payload;

    public JApiError(String target, Map<String, Object> payload) {
        super(target);
        this.target = target;
        this.payload = payload;
    }
}
