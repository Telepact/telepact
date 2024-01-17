package io.github.brenbar.uapi;

/**
 * Indicates critical failure to process a uAPI message.
 */
public class UApiProcessError extends RuntimeException {

    public UApiProcessError(String message) {
        super(message);
    }

    public UApiProcessError(Throwable cause) {
        super(cause);
    }
}
