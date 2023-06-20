package io.github.brenbar.japi;

import java.util.Map;

public class ApplicationError extends RuntimeException {
    public final String messageType;
    public final Map<String, Object> body;

    public ApplicationError(String messageType, Map<String, Object> body) {
        this.messageType = messageType;
        this.body = body;
    }
}
