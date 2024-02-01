package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.Map;

/**
 * A uAPI Message.
 */
public class Message {
    public final Map<String, Object> header;
    public final Map<String, Object> body;

    public Message(Map<String, Object> header, Map<String, Object> body) {
        this.header = new HashMap<>(header);
        this.body = body;
    }

    public String getBodyTarget() {
        var entry = _Util.unionEntry(body);
        return entry.getKey();
    }

    public Map<String, Object> getBodyPayload() {
        var entry = _Util.unionEntry(body);
        return (Map<String, Object>) entry.getValue();
    }
}
