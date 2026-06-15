//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

/**
 * Indicates failure to serialize a telepact Message.
 */
public class SerializationError extends RuntimeException {
    private final String context;

    /**
     * Constructs a SerializationError with the specified cause.
     *
     * @param cause the underlying cause of the error
     */
    public SerializationError(Throwable cause) {
        super(cause);
        this.context = null;
    }

    public SerializationError(Throwable cause, String context) {
        super("telepact serialization failed while " + context + ": " + cause.getMessage(), cause);
        this.context = context;
    }

    public String getContext() {
        return this.context;
    }
}
