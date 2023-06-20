package io.github.brenbar.japi;

public class ClientProcessError extends RuntimeException {
    public ClientProcessError(Throwable cause) {
        super(cause);
    }
}