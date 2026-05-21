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

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class UnpackBody {
    static Map<Object, Object> unpackBody(Map<Object, Object> body, BinaryEncoding binaryEncoding) {
        final var result = new HashMap<Object, Object>(body);

        for (final var packedSite : binaryEncoding.packedSites) {
            final var parentMap = getParentMap(result, packedSite.encodedPath);
            if (parentMap == null || packedSite.encodedPath.isEmpty()) {
                continue;
            }

            final var targetKey = packedSite.encodedPath.get(packedSite.encodedPath.size() - 1);
            final var value = parentMap.get(targetKey);
            if (value instanceof final List<?> listValue) {
                parentMap.put(targetKey, UnpackList.unpackList((List<Object>) listValue, packedSite.header));
            }
        }

        return result;
    }

    private static Map<Object, Object> getParentMap(Map<Object, Object> root, List<Integer> path) {
        Map<Object, Object> current = root;
        for (int index = 0; index < path.size() - 1; index += 1) {
            final var next = current.get(path.get(index));
            if (!(next instanceof final Map<?, ?> nextMap)) {
                return null;
            }
            current = (Map<Object, Object>) nextMap;
        }
        return current;
    }
}
