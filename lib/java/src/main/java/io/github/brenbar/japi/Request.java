package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;

/**
 * A helper class to build a jAPI Request.
 */
public class Request {
    public final String functionName;
    public final Map<String, Object> headers = new HashMap<>();
    public final Map<String, List<String>> selectedStructFields = new HashMap<>();
    public final Map<String, Object> functionArgument;
    public Optional<Boolean> useBinary = Optional.empty();
    public Optional<Boolean> forceSendJson = Optional.empty();
    public Optional<Long> timeoutMs = Optional.empty();

    /**
     * Construct the Request.
     * 
     * @param functionName
     * @param functionArgument
     */
    public Request(String functionName, Map<String, Object> functionArgument) {
        this.functionName = functionName;
        this.functionArgument = functionArgument;
    }

    /**
     * Indicate a struct that should only return the listed fields in the response
     * with the other fields omitted by the server.
     * 
     * @param struct
     * @param fields
     * @return
     */
    public Request selectStructFields(String struct, List<String> fields) {
        this.selectedStructFields.put(struct, fields);
        return this;
    }

    /**
     * Add a header to be included on the jAPI Request Message.
     * 
     * @param name
     * @param value
     * @return
     */
    public Request addHeader(String name, Object value) {
        this.headers.put(name, value);
        return this;
    }

    /**
     * Add a set of headers to be included on the jAPI Request Message.
     * 
     * @param headers
     * @return
     */
    public Request addHeaders(Map<String, Object> headers) {
        this.headers.putAll(headers);
        return this;
    }

    /**
     * Indicates if this request should use binary serialization.
     * 
     * Overrides the client default.
     * 
     * @param useBinary
     * @return
     */
    public Request setUseBinary(boolean useBinary) {
        this.useBinary = Optional.of(useBinary);
        return this;
    }

    /**
     * Indicates if this request should be sent as JSON, even if the response is
     * going to be received in binary.
     * 
     * Overrides the client default.
     * 
     * @param forceSendJson
     * @return
     */
    public Request setForceSendJson(boolean forceSendJson) {
        this.forceSendJson = Optional.of(forceSendJson);
        return this;
    }

    /**
     * Set the timeout for this request.
     * 
     * @param timeoutMs
     * @return
     */
    public Request setTimeoutMs(long timeoutMs) {
        this.timeoutMs = Optional.of(timeoutMs);
        return this;
    }
}