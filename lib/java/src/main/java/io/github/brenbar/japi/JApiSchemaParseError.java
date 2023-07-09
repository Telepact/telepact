package io.github.brenbar.japi;

public class JApiSchemaParseError extends RuntimeException {
    public JApiSchemaParseError(String message) {
        super(message);
    }

    public JApiSchemaParseError(String message, Throwable cause) {
        super(message, cause);
    }
}