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
 * A telepact Message.
 */
public class Message {
    public final Map<String, Object> headers;
    public final Map<String, Object> body;

    public Message(Map<String, Object> header, Map<String, Object> body) {
        this.headers = new HashMap<>(header);
        this.body = body;
    }

    public String getBodyTarget() {
        var entry = body.entrySet().stream().findAny().orElse(null);
        return entry.getKey();
    }

    public Map<String, Object> getBodyPayload() {
        var entry = body.entrySet().stream().findAny().orElse(null);
        return (Map<String, Object>) entry.getValue();
    }
}
