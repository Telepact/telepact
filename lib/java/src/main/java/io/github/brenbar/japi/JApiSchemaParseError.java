package io.github.brenbar.japi;

/**
 * Indicates a failure to parse a jAPI Schema.
 */
public class JApiSchemaParseError extends RuntimeException {
    public JApiSchemaParseError(String message) {
        super(message);
    }

    public JApiSchemaParseError(String message, Throwable cause) {
        super(message, cause);
    }
}