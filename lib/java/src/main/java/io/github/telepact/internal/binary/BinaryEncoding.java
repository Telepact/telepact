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

public class BinaryEncoding {

    public final Map<String, Integer> encodeMap;
    public final String[] decodeTable;
    public final Integer checksum;

    public BinaryEncoding(Map<String, Integer> binaryEncodingMap, Integer checksum) {
        this.encodeMap = binaryEncodingMap;
        this.decodeTable = new String[binaryEncodingMap.size()];
        for (final var entry : binaryEncodingMap.entrySet()) {
            final var keyId = entry.getValue();
            if (keyId < 0 || keyId >= this.decodeTable.length) {
                throw new IllegalArgumentException("Binary encoding ids must be dense sequential integers");
            }
            if (this.decodeTable[keyId] != null) {
                throw new IllegalArgumentException("Binary encoding ids must be unique");
            }
            this.decodeTable[keyId] = entry.getKey();
        }
        for (final var key : this.decodeTable) {
            if (key == null) {
                throw new IllegalArgumentException("Binary encoding ids must be dense sequential integers");
            }
        }
        this.checksum = checksum;
    }
}
