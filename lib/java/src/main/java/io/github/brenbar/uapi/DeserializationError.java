package io.github.brenbar.uapi;

/**
 * Indicates failure to deserialize of a uAPI message.
 */
public class DeserializationError extends RuntimeException {

    public DeserializationError(Throwable cause) {
        super(cause);
    }

    public DeserializationError(String message) {
        super(message);
    }

}