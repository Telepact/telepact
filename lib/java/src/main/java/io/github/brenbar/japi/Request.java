package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

public class Request {
    public final String functionName;
    public final Map<String, Object> headers = new HashMap<>();
    public final Map<String, List<String>> selectedStructFields = new HashMap<>();
    public final Map<String, Object> functionInput;
    public Optional<Boolean> useBinary = Optional.empty();
    public Optional<Boolean> forceSendJson = Optional.empty();

    public Request(String functionName, Map<String, Object> functionInput) {
        this.functionName = functionName;
        this.functionInput = functionInput;
    }

    public Request selectStructFields(String struct, List<String> fields) {
        this.selectedStructFields.put(struct, fields);
        return this;
    }

    public Request addHeader(String name, Object value) {
        this.headers.put(name, value);
        return this;
    }

    public Request addHeaders(Map<String, Object> headers) {
        this.headers.putAll(headers);
        return this;
    }

    public Request setUseBinary(boolean useBinary) {
        this.useBinary = Optional.of(useBinary);
        return this;
    }

    public Request setForceSendJson(boolean forceSendJson) {
        this.forceSendJson = Optional.of(forceSendJson);
        return this;
    }
}