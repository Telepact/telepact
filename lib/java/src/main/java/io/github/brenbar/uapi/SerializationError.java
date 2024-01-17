package io.github.brenbar.uapi;

/**
 * Indicates failure to serialize a uAPI Message.
 */
public class SerializationError extends RuntimeException {
    public SerializationError(Throwable cause) {
        super(cause);
    }
}
