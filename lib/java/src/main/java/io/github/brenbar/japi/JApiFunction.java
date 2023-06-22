package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

public class JApiFunction {
    public final String functionName;
    public final Map<String, Object> additionalHeaders = new HashMap<String, Object>();
    public final Map<String, Object> functionInput;
    public Optional<Boolean> useBinary = Optional.empty();
    public Optional<Boolean> forceSendJson = Optional.empty();

    public JApiFunction(String functionName, Map<String, Object> functionInput) {
        this.functionName = functionName;
        this.functionInput = functionInput;
    }

    public JApiFunction addHeader(String name, Object value) {
        additionalHeaders.put(name, value);
        return this;
    }

    public JApiFunction addHeaders(Map<String, Object> headers) {
        additionalHeaders.putAll(headers);
        return this;
    }

    public JApiFunction setUseBinary(boolean useBinary) {
        this.useBinary = Optional.of(useBinary);
        return this;
    }

    public JApiFunction setForceSendJson(boolean forceSendJson) {
        this.forceSendJson = Optional.of(forceSendJson);
        return this;
    }
}