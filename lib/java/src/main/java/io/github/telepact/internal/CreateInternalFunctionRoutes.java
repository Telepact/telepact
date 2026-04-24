//|
//|  Copyright The Telepact Authors
//|
//|  Licensed under the Apache License, Version 2.0 (the "License");
//|  you may not use this file except in compliance with the License.
//|  You may obtain a copy of the License at
//|
//|  https://www.apache.org/licenses/LICENSE-2.0
//|
//|  Unless required by applicable law or agreed to in writing, software
//|  distributed under the License is distributed on an "AS IS" BASIS,
//|  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//|  See the License for the specific language governing permissions and
//|  limitations under the License.
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
