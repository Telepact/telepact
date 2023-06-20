package io.github.brenbar.japi;

import java.util.Map;

public class ClientError extends RuntimeException {
    public final String type;
    public final Map<String, Object> body;

    public ClientError(String type, Map<String, Object> body) {
        super(type + ": " + body);
        this.type = type;
        this.body = body;
    }
}
