package io.github.brenbar.japi;

public class DeserializationException extends Exception {
    public final String target;

    public DeserializationException(String target, Throwable cause) {
        super(cause);
        this.target = target;
    }
}