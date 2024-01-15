package io.github.brenbar.uapi;

/**
 * Indicates a critical failure occurred during client-side processing of a jAPI
 * Request.
 */
public class ClientProcessError extends RuntimeException {
    public ClientProcessError(Throwable cause) {
        super(cause);
    }
}