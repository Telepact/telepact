package io.github.brenbar.japi.server;

public class JapiParseError extends RuntimeException {
    public JapiParseError(String message) {
        super(message);
    }
}