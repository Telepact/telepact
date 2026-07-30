//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
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
