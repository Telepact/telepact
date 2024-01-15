package io.github.brenbar.uapi;

/**
 * Indicates a failure occurred while serialization a uAPI Message.
 */
public class SerializationError extends RuntimeException {
    public SerializationError(Throwable cause) {
        super(cause);
    }
}
