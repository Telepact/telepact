//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

import java.util.UUID;

/**
 * Indicates critical failure in telepact processing logic.
 */
public class TelepactError extends RuntimeException {
    private final String kind;
    private final String caseId;

    /**
     * Constructs a new TelepactError with the specified detail message.
     *
     * @param message the detail message
     */
    public TelepactError(String message) {
        this(message, null, null, null);
    }

    /**
     * Constructs a new TelepactError with the specified cause.
     *
     * @param cause the cause of the error
     */
    public TelepactError(Throwable cause) {
        this(cause == null ? null : cause.getMessage(), null, cause, null);
    }

    public TelepactError(String message, String kind, Throwable cause) {
        this(message, kind, cause, null);
    }

    public TelepactError(String message, String kind) {
        this(message, kind, null, null);
    }

    public TelepactError(String message, String kind, Throwable cause, String caseId) {
        super(message, cause);
        this.kind = kind;
        this.caseId = caseId == null || caseId.isEmpty() ? UUID.randomUUID().toString() : caseId;
    }

    public TelepactError(String message, String kind, String caseId) {
        super(message);
        this.kind = kind;
        this.caseId = caseId == null || caseId.isEmpty() ? UUID.randomUUID().toString() : caseId;
    }

    public String getKind() {
        return this.kind;
    }

    public String getCaseId() {
        return this.caseId;
    }
}
