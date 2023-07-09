package io.github.brenbar.japi;

/**
 * Indicates deserialization of a jAPI message was unsuccessful.
 */
public class DeserializationError extends RuntimeException {

    public DeserializationError(Throwable cause) {
        super(cause);
    }
}