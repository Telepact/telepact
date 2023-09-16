package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.Map;

public class Message {
    public final Map<String, Object> header;
    public final Map<String, Map<String, Object>> body;

    public Message(Map<String, Object> header, Map<String, Map<String, Object>> body) {
        this.header = new HashMap<>(header);
        this.body = body;
    }

    public Message(Map<String, Map<String, Object>> body) {
        this.header = new HashMap<>();
        this.body = body;
    }
}
