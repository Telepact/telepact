package io.github.msgpact;

/**
 * Indicates critical failure in msgPact processing logic.
 */
public class MsgPactError extends RuntimeException {

    public MsgPactError(String message) {
        super(message);
    }

    public MsgPactError(Throwable cause) {
        super(cause);
    }
}
