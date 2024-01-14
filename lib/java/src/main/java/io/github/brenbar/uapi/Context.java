package io.github.brenbar.japi;

import java.util.Map;

/**
 * An object containing the function name and request headers from a server-side
 * Request handling.
 */
public class Context {
    public final String functionName;
    public final Map<String, Object> requestHeaders;

    public Context(String functionName, Map<String, Object> requestHeaders) {
        this.functionName = functionName;
        this.requestHeaders = requestHeaders;
    }
}