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

package io.github.telepact;

import java.util.HashMap;
import java.util.Map;

public class FunctionRouter {
    private static final class RegisteredFunction {
        private final boolean authenticated;
        private final ServerFunction handler;

        private RegisteredFunction(boolean authenticated, ServerFunction handler) {
            this.authenticated = authenticated;
            this.handler = handler;
        }
    }

    private final Map<String, RegisteredFunction> functions = new HashMap<>();

    public FunctionRouter register(String functionName, ServerFunction handler) {
        return this.registerUnauthenticated(functionName, handler);
    }

    public FunctionRouter registerUnauthenticated(String functionName, ServerFunction handler) {
        this.functions.put(functionName, new RegisteredFunction(false, handler));
        return this;
    }

    public FunctionRouter registerAuthenticated(String functionName, ServerFunction handler) {
        this.functions.put(functionName, new RegisteredFunction(true, handler));
        return this;
    }

    public Message route(Message requestMessage) {
        final var functionName = requestMessage.getBodyTarget();
        final var arguments = requestMessage.getBodyPayload();
        final var registration = this.functions.get(functionName);
        if (registration == null || registration.handler == null) {
            throw new IllegalArgumentException("Unknown function: " + functionName);
        }
        if (registration.authenticated) {
            final var authResult = requestMessage.headers.get("@result");
            if (authResult instanceof Map<?, ?> authMap) {
                return new Message(Map.of(), (Map<String, Object>) authMap);
            }
            if (!requestMessage.headers.containsKey("@auth_")) {
                return new Message(Map.of(), Map.of("ErrorUnauthenticated_", Map.of("message!", "Valid authentication is required.")));
            }
        }
        return registration.handler.apply(requestMessage.headers, arguments);
    }
}
