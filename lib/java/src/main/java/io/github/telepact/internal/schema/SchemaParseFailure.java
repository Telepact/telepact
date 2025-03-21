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

package io.github.telepact.internal.schema;

import java.util.List;
import java.util.Map;

public class SchemaParseFailure {
    public final String documentName;
    public final List<Object> path;
    public final String reason;
    public final Map<String, Object> data;

    public SchemaParseFailure(String documentName, List<Object> path, String reason, Map<String, Object> data) {
        this.documentName = documentName;
        this.path = path;
        this.reason = reason;
        this.data = data;
    }
}
