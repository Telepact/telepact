package io.github.brenbar.japi;

public class JApiProcessError extends RuntimeException {

    public JApiProcessError(String message) {
        super(message);
    }

    public JApiProcessError(Throwable cause) {
        super(cause);
    }
}
