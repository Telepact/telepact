package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.Map;

public class Message {
    public final Map<String, Object> header;
    public final Map<String, Object> body;

    public Message(Map<String, Object> header, Map<String, Object> body) {
        this.header = new HashMap<>(header);
        this.body = body;
    }

    public Message(Map<String, Object> header, String target, Map<String, Object> payload) {
        this.header = new HashMap<>(header);
        this.body = Map.of(target, payload);
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
        return body.keySet().stream().findAny().get();
    }

    public Map<String, Object> getBodyPayload() {
        return (Map<String, Object>) body.values().stream().findAny().get();
    }
}
