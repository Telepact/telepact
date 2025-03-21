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

package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.PackList.packList;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Pack {
    static Object pack(Object value) {
        if (value instanceof final List l) {
            return packList(l);
        } else if (value instanceof final Map<?, ?> m) {
            final var newMap = new HashMap<Object, Object>();

            for (final var entry : m.entrySet()) {
                newMap.put(entry.getKey(), pack(entry.getValue()));
            }

            return newMap;
        } else {
            return value;
        }
    }
}
