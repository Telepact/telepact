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
