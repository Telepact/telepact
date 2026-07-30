//|
//|  Copyright The Telepact Authors
//|  SPDX-License-Identifier: Apache-2.0
//|

package io.github.telepact.internal.binary;

import static io.github.telepact.internal.binary.EncodeBody.encodeBody;
import static io.github.telepact.internal.binary.PackBody.packBody;

import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Optional;

public class ClientBinaryEncode {
    static List<Object> clientBinaryEncode(List<Object> message, BinaryEncodingCache binaryEncodingCache,
            ClientBinaryStrategy binaryChecksumStrategy)
            throws BinaryEncoderUnavailableError {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var forceSendJson = headers.remove("_forceSendJson");

        final var checksums = binaryChecksumStrategy.getCurrentChecksums();
        headers.put("@bin_", checksums);


        if (Objects.equals(forceSendJson, true)) {
            throw new BinaryEncoderUnavailableError();
        }

        if (checksums.size() > 1) {
            throw new BinaryEncoderUnavailableError();
        }

        final Optional<BinaryEncoding> binaryEncodingOpt = checksums.size() > 0 ? binaryEncodingCache.get(checksums.get(0)) : Optional.empty();
        if (!binaryEncodingOpt.isPresent()) {
            throw new BinaryEncoderUnavailableError();
        }
        final BinaryEncoding binaryEncoding = binaryEncodingOpt.get();

        final var encodedMessageBody = encodeBody(messageBody, binaryEncoding);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("@pac_"))) {
            finalEncodedMessageBody = packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }
}
