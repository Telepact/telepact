package io.github.telepact;

/**
 * Indicates critical failure in telepact processing logic.
 */
public class TelepactError extends RuntimeException {

    public TelepactError(String message) {
        super(message);
    }

    public TelepactError(Throwable cause) {
        super(cause);
    }
}
