package io.github.brenbar.japi;

public class SerializationError extends RuntimeException {
    public SerializationError(Throwable cause) {
        super(cause);
    }
}
