//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal;

import java.util.Map;

import io.github.telepact.Message;
import io.github.telepact.TelepactError;

public final class UnknownError {
    private UnknownError() {
    }

    public static Message buildUnknownErrorMessage(TelepactError error, Map<String, Object> headers) {
        return new Message(headers, Map.of("ErrorUnknown_", Map.of("caseId", error.getCaseId())));
    }
}
