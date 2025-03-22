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

import static io.github.telepact.internal.binary.EncodeBody.encodeBody;
import static io.github.telepact.internal.binary.PackBody.packBody;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public class ServerBinaryEncode {
    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoding binaryEncoder) {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.remove("_clientKnownBinaryChecksums");

        final var resultTag = new ArrayList<>(messageBody.keySet()).get(0);

        if (!resultTag.equals("Ok_")) {
            throw new BinaryEncoderUnavailableError();
        }

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("@enc_", binaryEncoder.encodeMap);
        }

        headers.put("@bin_", List.of(binaryEncoder.checksum));
        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("@pac_"))) {
            finalEncodedMessageBody = packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }
}
