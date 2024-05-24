package io.github.brenbar.uapi.internal;

import java.util.List;
import java.util.Map;
import java.util.Objects;

import static io.github.brenbar.uapi.internal.DecodeBody.decodeBody;
import static io.github.brenbar.uapi.internal.UnpackBody.unpackBody;

public class ServerBinaryDecode {
    static List<Object> serverBinaryDecode(List<Object> message, _BinaryEncoding binaryEncoder) {
        final var headers = (Map<String, Object>) message.get(0);
        final var encodedMessageBody = (Map<Object, Object>) message.get(1);
        final var clientKnownBinaryChecksums = (List<Integer>) headers.get("bin_");
        final var binaryChecksumUsedByClientOnThisMessage = clientKnownBinaryChecksums.get(0);

        if (!Objects.equals(binaryChecksumUsedByClientOnThisMessage, binaryEncoder.checksum)) {
            throw new _BinaryEncoderUnavailableError();
        }

        final Map<Object, Object> finalEncodedMessageBody;
        if (Objects.equals(true, headers.get("_pac"))) {
            finalEncodedMessageBody = unpackBody(encodedMessageBody);
        } else {
            finalEncodedMessageBody = encodedMessageBody;
        }

        final var messageBody = (Map<String, Object>) decodeBody(finalEncodedMessageBody, binaryEncoder);
        return List.of(headers, messageBody);
    }
}
