package io.github.msgpact.internal.validation;

public class InvalidMessage extends RuntimeException {

    public InvalidMessage() {
        super();
    }

    public InvalidMessage(Throwable cause) {
        super(cause);
    }
}
