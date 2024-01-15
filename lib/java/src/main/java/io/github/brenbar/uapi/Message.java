package io.github.brenbar.uapi;

import java.util.HashMap;
import java.util.Map;

public class Message {
    public final Map<String, Object> header;
    public final Map<String, Object> body;

    public Message(Map<String, Object> header, Map<String, Object> body) {
        this.header = new HashMap<>(header);
        this.body = body;
    }

    public Message(Map<String, Object> body) {
        this.header = new HashMap<>();
        this.body = body;
    }

    public Message(String target, Map<String, Object> payload) {
        this.header = new HashMap<>();
        this.body = Map.of(target, payload);
    }

    public String getBodyTarget() {
        var entry = _UUnion.entry(body);
        return entry.getKey();
    }

    public Map<String, Object> getBodyPayload() {
        var entry = _UUnion.entry(body);
        return (Map<String, Object>) entry.getValue();
    }
}
