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

package io.github.telepact.example.javabinary;

import io.github.telepact.Message;
import io.github.telepact.Server;
import io.github.telepact.TelepactSchema;
import io.github.telepact.TelepactSchemaFiles;
import java.util.ArrayList;
import java.util.Map;

public final class Main {
    private Main() {}

    static Server buildTelepactServer() {
        var files = new TelepactSchemaFiles("api");
        var schema = TelepactSchema.fromFileJsonMap(files.filenamesToJson);
        var options = new Server.Options();
        options.authRequired = false;
        return new Server(schema, requestMessage -> {
            var functionName = requestMessage.getBodyTarget();
            if (!"fn.getNumbers".equals(functionName)) {
                throw new IllegalArgumentException("Unknown function: " + functionName);
            }
            var arguments = requestMessage.getBodyPayload();
            var limit = ((Number) arguments.get("limit")).intValue();
            var values = new ArrayList<Integer>();
            for (int i = 1; i <= limit; i += 1) {
                values.add(i);
            }
            return new Message(Map.of(), Map.of("Ok_", Map.of("values", values)));
        }, options);
    }

    static boolean looksLikeJson(byte[] bytes) {
        for (byte value : bytes) {
            if (!Character.isWhitespace(value)) {
                return value == '[' || value == '{';
            }
        }
        return false;
    }
}
