package io.github.brenbar.japi;

import java.util.HashMap;
import java.util.Map;

public class FnMessage {

    public final Map<String, Object> header;
    public final String target;
    public final Map<String, Object> payload;

    public FnMessage(Map<String, Object> header, String target, Map<String, Object> argument) {
        this.header = header;
        this.target = target;
        this.payload = argument;
    }

    public FnMessage(String target, Map<String, Object> argument) {
        this.header = new HashMap<>();
        this.target = target;
        this.payload = argument;
    }

}
