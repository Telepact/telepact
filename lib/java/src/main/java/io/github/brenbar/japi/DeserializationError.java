package io.github.brenbar.japi;

public class DeserializationError extends Exception {
    public final String target;

    public DeserializationError(String target, Throwable cause) {
        super(cause);
        this.target = target;
    }
}