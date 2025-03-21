package io.github.telepact;

/**
 * Indicates failure to serialize a telepact Message.
 */
public class SerializationError extends RuntimeException {
    public SerializationError(Throwable cause) {
        super(cause);
    }
}
