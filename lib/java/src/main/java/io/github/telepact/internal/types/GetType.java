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

package io.github.telepact.internal.types;

import java.util.List;
import java.util.Map;

public class GetType {

    public static String getType(Object value) {
        if (value == null) {
            return "Null";
        } else if (value instanceof Boolean) {
            return "Boolean";
        } else if (value instanceof Number) {
            return "Number";
        } else if (value instanceof String) {
            return "String";
        } else if (value instanceof List) {
            return "Array";
        } else if (value instanceof Map) {
            return "Object";
        } else {
            return "Unknown";
        }
    }
}
