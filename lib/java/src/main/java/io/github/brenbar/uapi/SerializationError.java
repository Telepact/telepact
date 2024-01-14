package io.github.brenbar.japi;

/**
 * Indicates a failure occurred while serialization a jAPI Message.
 */
public class SerializationError extends RuntimeException {
    public SerializationError(Throwable cause) {
        super(cause);
    }
}
