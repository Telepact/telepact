package io.github.brenbar.japi;

import java.util.Map;

public class Context {
    public final String functionName;
    public final Map<String, Object> requestHeaders;

    public Context(String functionName, Map<String, Object> requestHeaders) {
        this.functionName = functionName;
        this.requestHeaders = requestHeaders;
    }
}