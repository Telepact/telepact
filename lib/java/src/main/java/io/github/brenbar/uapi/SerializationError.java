package io.github.brenbar.uapi;

/**
 * Indicates a failure occurred while serialization a jAPI Message.
 */
public class SerializationError extends RuntimeException {
    public SerializationError(Throwable cause) {
        super(cause);
    }
}
