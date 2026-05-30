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

import io.github.telepact.Serialization;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

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

    @Override
    public byte[] encodeToMsgPack(List<Object> message, Serialization serializer) throws Throwable {
        if (!(serializer instanceof BinaryMsgPackSerialization binarySerialization)) {
            return BinaryEncoder.super.encodeToMsgPack(message, serializer);
        }

        final var headers = (Map<String, Object>) message.get(0);
        final var body = (Map<String, Object>) message.get(1);
        final var forceSendJson = headers.remove("_forceSendJson");
        final var checksums = this.binaryChecksumStrategy.getCurrentChecksums();
        headers.put("@bin_", checksums);

        if (Boolean.TRUE.equals(forceSendJson) || checksums.size() > 1) {
            throw new BinaryEncoderUnavailableError();
        }

        final var binaryEncoding = checksums.isEmpty() ? null : this.binaryEncodingCache.get(checksums.get(0)).orElse(null);
        if (binaryEncoding == null) {
            throw new BinaryEncoderUnavailableError();
        }

        return binarySerialization.toBinaryMsgPack(headers, body, binaryEncoding);
    }

    @Override
    public List<Object> decodeMsgPack(byte[] messageBytes, Serialization serializer) throws Throwable {
        if (!(serializer instanceof BinaryMsgPackSerialization binarySerialization)) {
            return BinaryEncoder.super.decodeMsgPack(messageBytes, serializer);
        }

        final var headers = binarySerialization.fromMsgPackHeaders(messageBytes);
        final var binaryChecksums = (List<Integer>) headers.headers().get("@bin_");
        final var binaryChecksum = binaryChecksums.get(0);

        if (headers.headers().containsKey("@enc_")) {
            this.binaryEncodingCache.add(binaryChecksum, toIntegerMap((Map<?, ?>) headers.headers().get("@enc_")));
        }

        this.binaryChecksumStrategy.updateChecksum(binaryChecksum);
        final var newCurrentChecksumStrategy = this.binaryChecksumStrategy.getCurrentChecksums();
        final var binaryEncoding = this.binaryEncodingCache.get(newCurrentChecksumStrategy.get(0)).get();
        final var body = binarySerialization.fromMsgPackBody(messageBytes, headers.bodyOffset(), binaryEncoding);
        return List.of(headers.headers(), body);
    }

    private static Map<String, Integer> toIntegerMap(Map<?, ?> raw) {
        final var result = new HashMap<String, Integer>(raw.size());
        for (final var entry : raw.entrySet()) {
            result.put((String) entry.getKey(), ((Number) entry.getValue()).intValue());
        }
        return result;
    }
}
