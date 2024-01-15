package io.github.brenbar.uapi;

/**
 * Indicates deserialization of a uAPI message was unsuccessful.
 */
public class DeserializationError extends RuntimeException {

    public DeserializationError(Throwable cause) {
        super(cause);
    }

    public DeserializationError(String message) {
        super(message);
    }

}