//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal;

import java.util.Map;
import java.util.TreeMap;

import io.github.telepact.FunctionRoute;
import io.github.telepact.Message;
import io.github.telepact.TelepactSchema;

public class CreateInternalFunctionRoutes {
    public static Map<String, FunctionRoute> createInternalFunctionRoutes(TelepactSchema telepactSchema) {
        return Map.of(
                "fn.ping_",
                (_functionName, _requestMessage) -> new Message(Map.of(), Map.of("Ok_", Map.of())),
                "fn.api_",
                (_functionName, requestMessage) -> {
                    final var requestPayload = new TreeMap<>(requestMessage.getBodyPayload());
                    final var includeInternal = Boolean.TRUE.equals(requestPayload.get("includeInternal!"));
                    final var includeExamples = Boolean.TRUE.equals(requestPayload.get("includeExamples!"));
                    final var apiDefinitions = includeExamples
                            ? GetApiDefinitionsWithExamples.getApiDefinitionsWithExamples(telepactSchema, includeInternal)
                            : includeInternal ? telepactSchema.full : telepactSchema.original;
                    return new Message(Map.of(), Map.of("Ok_", Map.of("api", apiDefinitions)));
                });
    }
}
