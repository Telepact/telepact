//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.ClientBinaryDecode.clientBinaryDecode;
import static io.github.telepact.internal.binary.ClientBinaryEncode.clientBinaryEncode;

import java.util.List;

public class ClientBinaryEncoder implements BinaryEncoder {

    private final BinaryEncodingCache binaryEncodingCache;
    private final ClientBinaryStrategy binaryChecksumStrategy;

    public ClientBinaryEncoder(BinaryEncodingCache binaryEncodingCache) {
        this.binaryEncodingCache = binaryEncodingCache;
        this.binaryChecksumStrategy = new ClientBinaryStrategy(binaryEncodingCache);
    }

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return clientBinaryEncode(message, this.binaryEncodingCache,
                this.binaryChecksumStrategy);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return clientBinaryDecode(message, this.binaryEncodingCache, this.binaryChecksumStrategy);
    }
}