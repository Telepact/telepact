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

import java.util.Map;
import java.util.Optional;

public interface BinaryEncodingCache {

    /**
     * Set a binary encoding in the cache.
     * @param checksum The checksum of the binary encoding.
     * @param binaryEncodingMap The binary encoding map.
     */
    void add(int checksum, Map<String, Integer> binaryEncodingMap);

    /**
     * Get a binary encoding from the cache.
     * @param checksum The checksum of the binary encoding.
     * @return The binary encoding.
     */
    Optional<BinaryEncoding> get(int checksum);

    /**
     * Delete a binary encoding from the cache.
     * @param checksum The checksum of the binary encoding.
     */
    void remove(int checksum);
}
