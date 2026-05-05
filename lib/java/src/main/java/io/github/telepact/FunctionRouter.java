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

/**
 * Routes a request message to the configured function route for its body
 * target.
 */
public class FunctionRouter {
    private final Map<String, FunctionRoute> authenticatedFunctionRoutes;
    private final Map<String, FunctionRoute> unauthenticatedFunctionRoutes;

    public FunctionRouter() {
        this.authenticatedFunctionRoutes = new HashMap<>();
        this.unauthenticatedFunctionRoutes = new HashMap<>();
    }

    public void registerRoutes(Map<String, FunctionRoute> functionRoutes) {
        registerUnauthenticatedRoutes(functionRoutes);
    }

    public void registerAuthenticatedRoutes(Map<String, FunctionRoute> functionRoutes) {
        for (var entry : functionRoutes.entrySet()) {
            this.authenticatedFunctionRoutes.put(entry.getKey(), entry.getValue());
            this.unauthenticatedFunctionRoutes.remove(entry.getKey());
        }
    }

    public void registerUnauthenticatedRoutes(Map<String, FunctionRoute> functionRoutes) {
        for (var entry : functionRoutes.entrySet()) {
            this.unauthenticatedFunctionRoutes.put(entry.getKey(), entry.getValue());
            this.authenticatedFunctionRoutes.remove(entry.getKey());
        }
    }

    public boolean requiresAuthentication(String functionName) {
        return this.authenticatedFunctionRoutes.containsKey(functionName);
    }

    public boolean hasAuthenticatedRoutes() {
        return !this.authenticatedFunctionRoutes.isEmpty();
    }

    public Message route(Message requestMessage) {
        final var functionName = requestMessage.getBodyTarget();
        final var functionRoute = this.authenticatedFunctionRoutes.containsKey(functionName)
                ? this.authenticatedFunctionRoutes.get(functionName)
                : this.unauthenticatedFunctionRoutes.get(functionName);
        if (functionRoute == null) {
            throw new IllegalArgumentException("Unknown function: " + functionName);
        }
        return functionRoute.apply(functionName, requestMessage);
    }
}
