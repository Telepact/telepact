package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import static io.github.brenbar.uapi.internal.EncodeBody.encodeBody;
import static io.github.brenbar.uapi.internal.PackBody.packBody;

public class ServerBinaryEncode {
    static List<Object> serverBinaryEncode(List<Object> message, BinaryEncoding binaryEncoder) {
        final var headers = (Map<String, Object>) message.get(0);
        final var messageBody = (Map<String, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.remove("_clientKnownBinaryChecksums");

        if (clientKnownBinaryChecksums == null || !clientKnownBinaryChecksums.contains(binaryEncoder.checksum)) {
            headers.put("enc_", binaryEncoder.encodeMap);
        }

        headers.put("bin_", List.of(binaryEncoder.checksum));
        final var encodedMessageBody = encodeBody(messageBody, binaryEncoder);

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = packBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        return List.of(headers, finalEncodedMessageBody);
    }
}
