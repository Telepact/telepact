package io.github.brenbar.uapi;

import java.util.List;

public class MessageParseError extends RuntimeException {
    public final List<String> failures;

    public MessageParseError(List<String> failures) {
        super(String.valueOf(failures));
        this.failures = failures;
    }
}
