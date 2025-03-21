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

import static io.github.telepact.internal.binary.ClientBinaryDecode.clientBinaryDecode;
import static io.github.telepact.internal.binary.ClientBinaryEncode.clientBinaryEncode;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

import io.github.telepact.ClientBinaryStrategy;

public class ClientBinaryEncoder implements BinaryEncoder {

    private final Map<Integer, BinaryEncoding> recentBinaryEncoders;
    private final ClientBinaryStrategy binaryChecksumStrategy;

    public ClientBinaryEncoder(ClientBinaryStrategy binaryChecksumStrategy) {
        this.recentBinaryEncoders = new ConcurrentHashMap<>();
        this.binaryChecksumStrategy = binaryChecksumStrategy;
    }

    @Override
    public List<Object> encode(List<Object> message) throws BinaryEncoderUnavailableError {
        return clientBinaryEncode(message, this.recentBinaryEncoders,
                this.binaryChecksumStrategy);
    }

    @Override
    public List<Object> decode(List<Object> message) throws BinaryEncoderUnavailableError {
        return clientBinaryDecode(message, this.recentBinaryEncoders, this.binaryChecksumStrategy);
    }

}