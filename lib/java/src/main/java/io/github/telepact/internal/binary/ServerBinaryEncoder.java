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

import io.github.telepact.Serialization;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class ServerBinaryEncoder implements BinaryEncoder {

    private final BinaryEncoding binaryEncoder;

    public ServerBinaryEncoder(BinaryEncoding binaryEncoder) {
        this.binaryEncoder = binaryEncoder;
    }

    @Override
    public byte[] encodeToMsgPack(List<Object> message, Serialization serializer) throws Throwable {
        if (!(serializer instanceof BinaryMsgPackSerialization binarySerialization)) {
            throw new IllegalArgumentException("binary MsgPack serialization is required");
        }
        if (binaryEncoder == null) {
            throw new BinaryEncoderUnavailableError();
        }

        final var headers = (Map<String, Object>) message.get(0);
        final var body = (Map<String, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.remove("@clientKnownBinaryChecksums_");
        final var resultTag = body.keySet().iterator().next();

        if (!Objects.equals(resultTag, "Ok_")) {
            throw new BinaryEncoderUnavailableError();
        }

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("@enc_", binaryEncoder.encodeMap);
        }

        headers.put("@bin_", List.of(binaryEncoder.checksum));
        return binarySerialization.toBinaryMsgPack(headers, body, binaryEncoder);
    }

    @Override
    public List<Object> decodeMsgPack(byte[] messageBytes, Serialization serializer) throws Throwable {
        if (!(serializer instanceof BinaryMsgPackSerialization binarySerialization)) {
            throw new IllegalArgumentException("binary MsgPack serialization is required");
        }

        final var headers = binarySerialization.fromMsgPackHeaders(messageBytes);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.headers().get("@bin_");
        final var binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums.get(0);

        if (!Objects.equals(binaryChecksumUsedByClientOnThisMessage, binaryEncoder.checksum)) {
            throw new BinaryEncoderUnavailableError();
        }

        final var body = binarySerialization.fromMsgPackBody(messageBytes, headers.bodyOffset(), binaryEncoder);
        return List.of(headers.headers(), body);
    }
}
