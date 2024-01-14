package io.github.brenbar.japi;

public class UApiProcessError extends RuntimeException {

    public UApiProcessError(String message) {
        super(message);
    }

    public UApiProcessError(Throwable cause) {
        super(cause);
    }
}
