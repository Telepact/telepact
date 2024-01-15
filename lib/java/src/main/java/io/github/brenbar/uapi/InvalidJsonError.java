package io.github.brenbar.uapi;

/**
 * Indicates a failure to parse a jAPI Message due invalid JSON.
 */
public class InvalidJsonError extends Exception {

    public InvalidJsonError(Throwable cause) {
        super(cause);
    }
}
