package io.github.msgpact;

/**
 * Indicates failure to serialize a msgPact Message.
 */
public class SerializationError extends RuntimeException {
    public SerializationError(Throwable cause) {
        super(cause);
    }
}
