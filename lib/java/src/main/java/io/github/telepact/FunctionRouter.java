//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact;

import java.util.HashMap;
import java.util.Map;

/**
 * Routes a request message to the configured function route for its body
 * target.
 */
public class FunctionRouter {
    private final Map<String, FunctionRoute> functionRoutes;

    public FunctionRouter(Map<String, FunctionRoute> functionRoutes) {
        this.functionRoutes = functionRoutes == null ? new HashMap<>() : new HashMap<>(functionRoutes);
    }

    public Message route(Message requestMessage) {
        final var functionName = requestMessage.getBodyTarget();
        final var functionRoute = this.functionRoutes.get(functionName);
        if (functionRoute == null) {
            throw new IllegalArgumentException("Unknown function: " + functionName);
        }
        return functionRoute.apply(functionName, requestMessage);
    }

    Map<String, FunctionRoute> functionRoutes() {
        return this.functionRoutes;
    }
}
