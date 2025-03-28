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

import static io.github.telepact.internal.binary.DecodeBody.decodeBody;
import static io.github.telepact.internal.binary.UnpackBody.unpackBody;

import java.util.List;
import java.util.Map;
import java.util.Objects;

public class ClientBinaryDecode {
    static List<Object> clientBinaryDecode(List<Object> message, BinaryEncodingCache binaryEncodingCache,
            ClientBinaryStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var encodedMessageBody = (Map<Object, Object>) message.get(1);
        final var binaryChecksums = (List<Integer>) headers.get("@bin_");
        final var binaryChecksum = binaryChecksums.get(0);

        // If there is a binary encoding included on this message, cache it
        if (headers.containsKey("@enc_")) {
            final var binaryEncoding = (Map<String, Integer>) headers.get("@enc_");

            binaryEncodingCache.add(binaryChecksum, binaryEncoding);
        }

        binaryChecksumStrategy.updateChecksum(binaryChecksum);
        final var newCurrentChecksumStrategy = binaryChecksumStrategy.getCurrentChecksums();

        final var binaryEncoder = binaryEncodingCache.get(newCurrentChecksumStrategy.get(0)).get();

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("@pac_"))) {
            finalEncodedMessageBody = unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }
}
