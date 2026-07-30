//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal;

import java.util.Map;

import io.github.telepact.TelepactSchema;

public final class RequiresAuthentication {
    private RequiresAuthentication() {
    }

    public static boolean requiresAuthentication(TelepactSchema telepactSchema, String functionName) {
        Map<String, Object> functionDefinition = null;
        for (var definition : telepactSchema.full) {
            if (!(definition instanceof Map<?, ?> definitionMap) || !definitionMap.containsKey(functionName)) {
                continue;
            }
            functionDefinition = (Map<String, Object>) definitionMap;
            break;
        }

        if (functionName.endsWith("_") || Boolean.TRUE.equals(functionDefinition != null ? functionDefinition.get("$internal") : null)) {
            return false;
        }
        if (!telepactSchema.parsed.containsKey("union.Auth_")) {
            return false;
        }
        return !Boolean.FALSE.equals(functionDefinition != null ? functionDefinition.get("$authenticated") : null);
    }
}
