package io.github.brenbar.japi;

public class JapiParseError extends RuntimeException {
    public JapiParseError(String message) {
        super(message);
    }

    public JapiParseError(String message, Throwable cause) {
        super(message, cause);
    }
}