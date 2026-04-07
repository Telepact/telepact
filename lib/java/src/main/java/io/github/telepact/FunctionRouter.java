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
    private final Map<String, ServerFunction> functions = new HashMap<>();

    public FunctionRouter register(String functionName, ServerFunction handler) {
        this.functions.put(functionName, handler);
        return this;
    }

    public Message middleware(Map<String, Object> headers, String functionName, Map<String, Object> arguments, ServerNext next) {
        final var handler = this.functions.get(functionName);
        if (handler != null) {
            return handler.apply(headers, arguments);
        }
        return next.apply(headers, functionName, arguments);
    }
}
