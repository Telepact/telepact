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

    public final Map<String, Object> result;

    public JApiError(Map<String, Object> result) {
        super(String.valueOf(result));
        this.result = result;
    }
}
