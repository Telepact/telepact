package io.github.brenbar.uapi;

public class UApiProcessError extends RuntimeException {

    public UApiProcessError(String message) {
        super(message);
    }

    public UApiProcessError(Throwable cause) {
        super(cause);
    }
}
