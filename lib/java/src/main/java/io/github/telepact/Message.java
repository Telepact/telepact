package io.github.telepact;

import java.util.HashMap;
import java.util.Map;

/**
 * A telepact Message.
 */
public class Message {
    public final Map<String, Object> headers;
    public final Map<String, Object> body;

    public Message(Map<String, Object> header, Map<String, Object> body) {
        this.headers = new HashMap<>(header);
        this.body = body;
    }

    public String getBodyTarget() {
        var entry = body.entrySet().stream().findAny().orElse(null);
        return entry.getKey();
    }

    public Map<String, Object> getBodyPayload() {
        var entry = body.entrySet().stream().findAny().orElse(null);
        return (Map<String, Object>) entry.getValue();
    }
}
