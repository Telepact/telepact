package io.github.brenbar.japi;

import java.util.Map;

public class ApplicationFailure extends RuntimeException {
    public final String messageType;
    public final Map<String, Object> body;

    public ApplicationFailure(String messageType, Map<String, Object> body) {
        this.messageType = messageType;
        this.body = body;
    }
}
